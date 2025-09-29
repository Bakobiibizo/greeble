from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .manifest import Component, Manifest, ManifestError, default_manifest_path, load_manifest
from .scaffold import (
    CopyPlan,
    ScaffoldError,
    backup_existing_files,
    build_copy_plan,
    component_sources,
    ensure_within_project,
    execute_plan,
    remove_files,
)
from .starter import StarterError, scaffold_starter


def _resolve_project_dirs(
    project_root: Path | None, args: argparse.Namespace
) -> tuple[Path | None, Path | None, Path | None]:
    """Return (templates_dir, static_dir, docs_dir) given optional project_root and args.

    When project_root is None, returns (None, None, None). Docs dir is only returned
    when include_docs is True; otherwise None.
    """
    if project_root is None:
        return None, None, None
    templates_dir = project_root / Path(args.templates)
    static_dir = project_root / Path(args.static)
    docs_dir = project_root / Path(args.docs) if getattr(args, "include_docs", False) else None
    return templates_dir, static_dir, docs_dir


def _load_manifest(path: str | None) -> Manifest:
    manifest_path = Path(path) if path else default_manifest_path()
    return load_manifest(manifest_path)


def _render_plan(plans: Sequence[CopyPlan]) -> str:
    lines = ["Files to copy:"]
    lines.extend(f"  - {plan.source} -> {plan.destination}" for plan in plans)
    return "\n".join(lines)


def _print_project_status(
    project_root: Path,
    templates_dir: Path,
    static_dir: Path,
    docs_dir: Path | None,
) -> None:
    print(f"Project root: {project_root}")
    templates_status = "exists" if templates_dir.exists() else "missing"
    static_status = "exists" if static_dir.exists() else "missing"
    print(f"  Templates dir: {templates_dir} ({templates_status})")
    print(f"  Static dir: {static_dir} ({static_status})")
    if docs_dir is not None:
        docs_status = "exists" if docs_dir.exists() else "missing"
        print(f"  Docs dir: {docs_dir} ({docs_status})")


def _build_doctor_report(
    manifest: Manifest,
    *,
    project_root: Path | None,
    templates_dir: Path | None,
    static_dir: Path | None,
    docs_dir: Path | None,
    include_docs: bool,
) -> dict[str, object]:
    tokens_value = manifest.library.get("tokens_file")
    tokens_declared = isinstance(tokens_value, str)
    tokens_path = manifest.tokens_file if tokens_declared else None
    tokens_exists = tokens_path.exists() if tokens_path else False
    if tokens_declared and tokens_exists:
        tokens_status = "ok"
    elif tokens_declared:
        tokens_status = "warning"
    else:
        tokens_status = "info"

    warnings: list[dict[str, object]] = []
    if tokens_status == "warning":
        warnings.append(
            {
                "kind": "tokens",
                "level": "warning",
                "message": "Tokens file not found",
                "path": tokens_path,
            }
        )
    elif tokens_status == "info":
        warnings.append(
            {
                "kind": "tokens",
                "level": "info",
                "message": "Manifest does not declare library.tokens_file",
                "path": None,
            }
        )

    missing_sources: list[dict[str, object]] = []
    total_sources = 0
    for key in sorted(manifest.keys()):
        component = manifest.get(key)
        sources = component_sources(manifest, component)
        total_sources += len(sources)
        if missing := [source for source in sources if not source.exists()]:
            missing_sources.append({"component": component.key, "sources": missing})

    project_info: dict[str, object] | None = None
    if project_root is not None:
        root_exists = project_root.exists()
        paths_info: list[dict[str, object]] = []
        entries: list[tuple[str, Path | None]] = [
            ("templates", templates_dir),
            ("static", static_dir),
        ]
        if include_docs and docs_dir is not None:
            entries.append(("docs", docs_dir))
        if not root_exists:
            warnings.append(
                {
                    "kind": "project_root",
                    "level": "warning",
                    "message": "Project root does not exist",
                    "path": project_root,
                }
            )
        for kind, path in entries:
            if path is None:
                continue
            exists = path.exists()
            status = "ok" if exists else "warning"
            if status == "warning":
                warnings.append(
                    {
                        "kind": f"project_{kind}",
                        "level": "warning",
                        "message": f"{kind} directory missing",
                        "path": path,
                    }
                )
            relative = None
            if root_exists:
                try:
                    relative = path.relative_to(project_root)
                except ValueError:  # pragma: no cover - defensive
                    relative = None
            paths_info.append(
                {
                    "kind": kind,
                    "path": path,
                    "relative": relative,
                    "exists": exists,
                    "status": status,
                }
            )
        project_info = {
            "root": project_root,
            "exists": root_exists,
            "paths": paths_info,
        }

    summary = {
        "components_checked": len(manifest.components),
        "sources_checked": total_sources,
        "errors": len(missing_sources),
        "warnings": sum(w.get("level") == "warning" for w in warnings),
        "infos": sum(w.get("level") == "info" for w in warnings),
    }

    status = "ok" if summary["errors"] == 0 else "error"

    return {
        "status": status,
        "summary": summary,
        "manifest": {"path": manifest.path, "version": manifest.version},
        "tokens": {
            "declared": tokens_declared,
            "path": tokens_path,
            "status": tokens_status,
            "exists": tokens_exists if tokens_declared else None,
        },
        "components": {
            "total": len(manifest.components),
            "missing_sources": missing_sources,
        },
        "project": project_info,
        "warnings": warnings,
    }


def cmd_list(args: argparse.Namespace, manifest: Manifest) -> int:
    components = [manifest.get(key) for key in sorted(manifest.keys())]

    if getattr(args, "json", False):
        payload = {
            "total": len(components),
            "components": [
                {
                    "key": component.key,
                    "title": component.title,
                    "summary": component.summary,
                    "files": list(component.files),
                }
                for component in components
            ],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print("Available components:\n")
    for component in components:
        print(f"- {component.key}: {component.title} — {component.summary}")
    return 0


def _copy_component(
    *,
    manifest: Manifest,
    component: Component,
    project_root: Path,
    templates: Path,
    static: Path,
    docs: Path | None,
    include_docs: bool,
    force: bool,
    dry_run: bool,
) -> list[Path]:
    plans = build_copy_plan(
        manifest=manifest,
        component=component,
        project_root=project_root,
        templates_dir=templates,
        static_dir=static,
        include_docs=include_docs,
        docs_dir=docs,
    )
    ensure_within_project(project_root, plans)
    if dry_run:
        print(_render_plan(plans))
        return []
    return execute_plan(plans, force=force, dry_run=False)


def cmd_add(args: argparse.Namespace, manifest: Manifest) -> int:
    try:
        component = manifest.get(args.component)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    project_root = Path(args.project).resolve()
    templates_dir = Path(args.templates)
    static_dir = Path(args.static)
    docs_dir: Path | None = args.docs

    try:
        written = _copy_component(
            manifest=manifest,
            component=component,
            project_root=project_root,
            templates=templates_dir,
            static=static_dir,
            docs=docs_dir,
            include_docs=args.include_docs,
            force=args.force,
            dry_run=args.dry_run,
        )
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        return 0

    print(f"Copied {len(written)} file(s):")
    for path in written:
        rel = path.relative_to(project_root)
        print(f"  - {rel}")
    return 0


def _is_directory_non_empty(path: Path) -> bool:
    if not path.exists():
        return False
    if not path.is_dir():
        raise ScaffoldError(f"Destination exists and is not a directory: {path}")
    return any(path.iterdir())


def cmd_new(args: argparse.Namespace, manifest: Manifest) -> int:
    project_root = Path(args.project).resolve()
    docs_dir: Path = args.docs

    try:
        non_empty = _is_directory_non_empty(project_root)
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if non_empty and not args.force:
        print(
            "error: destination is not empty; re-run with --force to overwrite",
            file=sys.stderr,
        )
        return 2

    if not args.dry_run:
        project_root.mkdir(parents=True, exist_ok=True)

    try:
        plan = scaffold_starter(
            manifest=manifest,
            project_root=project_root,
            include_docs=args.include_docs,
            docs_dir=docs_dir,
            force=args.force,
            dry_run=args.dry_run,
        )
    except (ScaffoldError, StarterError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    destinations = {
        path.relative_to(project_root) for path in [*plan.project_files, *plan.component_files]
    }
    lines = sorted(destinations, key=lambda p: tuple(p.parts))

    if args.dry_run:
        print("Starter files that would be created:\n")
        for rel in lines:
            print(f"  - {rel}")
        return 0

    print(f"Starter project created at {project_root}")
    print(f"  + {len(plan.project_files)} starter files")
    print(f"  + {len(plan.component_files)} component assets")
    print("\nKey files:")
    for rel in lines[: min(10, len(lines))]:
        print(f"  - {rel}")
    if len(lines) > 10:
        print(f"  … {len(lines) - 10} more")
    return 0


def cmd_sync(args: argparse.Namespace, manifest: Manifest) -> int:
    try:
        component = manifest.get(args.component)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    project_root = Path(args.project).resolve()
    templates_dir = Path(args.templates)
    static_dir = Path(args.static)
    docs_dir: Path | None = args.docs
    try:
        plans = build_copy_plan(
            manifest=manifest,
            component=component,
            project_root=project_root,
            templates_dir=templates_dir,
            static_dir=static_dir,
            docs_dir=docs_dir,
            include_docs=args.include_docs,
        )
        ensure_within_project(project_root, plans)
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(_render_plan(plans))
        if args.backup:
            existing = [plan.destination for plan in plans if plan.destination.exists()]
            if existing:
                print("\nBackups that would be created:")
                for dest in existing:
                    try:
                        rel = dest.relative_to(project_root)
                    except ValueError:  # pragma: no cover - defensive
                        rel = dest
                    print(f"  - {rel}")
        return 0

    try:
        backups: list[Path] = []
        if args.backup:
            backups = backup_existing_files(plans)
        written = execute_plan(plans, force=True, dry_run=False)
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Synced {len(written)} file(s).")
    if args.backup and backups:
        print(f"Created {len(backups)} backup file(s):")
        for path in backups:
            try:
                rel = path.relative_to(project_root)
            except ValueError:  # pragma: no cover - defensive
                rel = path
            print(f"  - {rel}")
    return 0


def cmd_remove(args: argparse.Namespace, manifest: Manifest) -> int:
    try:
        component = manifest.get(args.component)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    project_root = Path(args.project).resolve()
    templates_dir = Path(args.templates)
    static_dir = Path(args.static)
    docs_dir: Path | None = args.docs

    try:
        plans = build_copy_plan(
            manifest=manifest,
            component=component,
            project_root=project_root,
            templates_dir=templates_dir,
            static_dir=static_dir,
            docs_dir=docs_dir,
            include_docs=args.include_docs,
        )
        ensure_within_project(project_root, plans)
        if args.dry_run:
            print("Files that would be removed:\n")
            for plan in plans:
                rel = plan.destination.relative_to(project_root)
                print(f"  - {rel}")
            return 0
        removed, missing = remove_files(plans, dry_run=False)
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(f"Removed {len(removed)} file(s).")
    for path in removed:
        print(f"  - {path.relative_to(project_root)}")
    if missing:
        print("Skipped missing files:")
        for path in missing:
            print(f"  - {path.relative_to(project_root)}")
    return 0


def cmd_doctor(args: argparse.Namespace, manifest: Manifest) -> int:
    # JSON mode: generate a structured report and print it
    if getattr(args, "json", False):
        project_root = Path(args.project).resolve() if args.project else None
        templates_dir, static_dir, docs_dir = _resolve_project_dirs(project_root, args)
        report = _build_doctor_report(
            manifest,
            project_root=project_root,
            templates_dir=templates_dir,
            static_dir=static_dir,
            docs_dir=docs_dir,
            include_docs=args.include_docs,
        )
        print(json.dumps(report, indent=2, default=str))
        return 0 if report.get("status") == "ok" else 1

    # Human-readable mode
    ok = True
    print(f"Manifest path: {default_manifest_path()}")
    tokens = manifest.tokens_file
    if tokens and tokens.exists():
        print(f"✔ Tokens file referenced by manifest: {tokens}")
    elif tokens:
        print(f"! Tokens file not found at {tokens} (ensure it is installed in your project)")
    else:
        print("! Manifest does not declare library.tokens_file")

    for key in sorted(manifest.keys()):
        component = manifest.get(key)
        for source in component_sources(manifest, component):
            if not source.exists():
                print(f"✖ Missing source for {component.key}: {source}")
                ok = False

    project_root = Path(args.project).resolve() if args.project else None
    if project_root:
        templates_dir_opt, static_dir_opt, docs_dir = _resolve_project_dirs(project_root, args)
        # Narrow optionals for mypy – when project_root is provided, these are Paths
        assert templates_dir_opt is not None and static_dir_opt is not None
        _print_project_status(project_root, templates_dir_opt, static_dir_opt, docs_dir)

    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="greeble", description="Greeble component CLI")
    parser.add_argument(
        "--manifest",
        help="Path to greeble.manifest.yaml (defaults to repository root)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub_list = sub.add_parser("list", help="List available components")
    sub_list.set_defaults(func=cmd_list)
    sub_list.add_argument("--json", action="store_true", help="Output JSON payload of components")

    sub_new = sub.add_parser("new", help="Scaffold a new Greeble starter project")
    sub_new.add_argument(
        "project",
        type=Path,
        help="Destination directory for the starter project",
    )
    sub_new.add_argument(
        "--include-docs",
        action="store_true",
        help="Copy component documentation alongside templates/static",
    )
    sub_new.add_argument(
        "--docs",
        default=Path("docs"),
        type=Path,
        help="Docs root relative to project (defaults to 'docs')",
    )
    sub_new.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files in the destination",
    )
    sub_new.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the files that would be created",
    )
    sub_new.set_defaults(func=cmd_new)

    sub_add = sub.add_parser("add", help="Copy a component into your project")
    sub_add.add_argument("component", help="Component key to add (see `greeble list`)")
    sub_add.add_argument(
        "--project",
        default=Path.cwd(),
        type=Path,
        help="Destination project root (default: current directory)",
    )
    sub_add.add_argument(
        "--templates",
        default=Path("templates"),
        type=Path,
        help="Templates root relative to project (defaults to 'templates')",
    )
    sub_add.add_argument(
        "--static",
        default=Path("static"),
        type=Path,
        help="Static assets root relative to project (defaults to 'static')",
    )
    sub_add.add_argument(
        "--docs",
        default=Path("docs"),
        type=Path,
        help="Docs root relative to project (defaults to 'docs')",
    )
    sub_add.add_argument(
        "--include-docs",
        action="store_true",
        help="Copy component documentation files as well",
    )
    sub_add.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )
    sub_add.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the files that would be copied without writing them",
    )
    sub_add.set_defaults(func=cmd_add)

    sub_sync = sub.add_parser("sync", help="Re-copy a component, overwriting existing files")
    sub_sync.add_argument("component", help="Component key to sync")
    sub_sync.add_argument(
        "--project",
        default=Path.cwd(),
        type=Path,
        help="Destination project root (default: current directory)",
    )
    sub_sync.add_argument(
        "--templates",
        default=Path("templates"),
        type=Path,
        help="Templates root relative to project",
    )
    sub_sync.add_argument(
        "--static",
        default=Path("static"),
        type=Path,
        help="Static root relative to project",
    )
    sub_sync.add_argument(
        "--docs",
        default=Path("docs"),
        type=Path,
        help="Docs root relative to project",
    )
    sub_sync.add_argument(
        "--include-docs",
        action="store_true",
        help="Sync documentation files alongside templates/static",
    )
    sub_sync.add_argument(
        "--backup",
        action="store_true",
        help="Create backups of existing files before overwriting",
    )
    sub_sync.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing",
    )
    sub_sync.set_defaults(func=cmd_sync)

    sub_remove = sub.add_parser("remove", help="Remove a component's files from your project")
    sub_remove.add_argument("component", help="Component key to remove")
    sub_remove.add_argument(
        "--project",
        default=Path.cwd(),
        type=Path,
        help="Destination project root (default: current directory)",
    )
    sub_remove.add_argument(
        "--templates",
        default=Path("templates"),
        type=Path,
        help="Templates root relative to project",
    )
    sub_remove.add_argument(
        "--static",
        default=Path("static"),
        type=Path,
        help="Static root relative to project",
    )
    sub_remove.add_argument(
        "--docs",
        default=Path("docs"),
        type=Path,
        help="Docs root relative to project",
    )
    sub_remove.add_argument(
        "--include-docs",
        action="store_true",
        help="Remove documentation files as well",
    )
    sub_remove.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without deleting files",
    )
    sub_remove.set_defaults(func=cmd_remove)

    sub_doctor = sub.add_parser("doctor", help="Validate manifest and project setup")
    sub_doctor.add_argument(
        "--project",
        type=Path,
        help="Optional project root to inspect",
    )
    sub_doctor.add_argument(
        "--templates",
        default=Path("templates"),
        type=Path,
        help="Templates root relative to project",
    )
    sub_doctor.add_argument(
        "--static",
        default=Path("static"),
        type=Path,
        help="Static root relative to project",
    )
    sub_doctor.add_argument(
        "--include-docs",
        action="store_true",
        help="Report on docs directory when project root supplied",
    )
    sub_doctor.add_argument(
        "--docs",
        default=Path("docs"),
        type=Path,
        help="Docs root relative to project",
    )
    sub_doctor.add_argument(
        "--json",
        action="store_true",
        help="Emit a structured JSON report to stdout",
    )
    sub_doctor.set_defaults(func=cmd_doctor)

    # Theme & Tailwind helpers
    sub_theme = sub.add_parser("theme", help="Theme and Tailwind helpers")
    theme_sub = sub_theme.add_subparsers(dest="theme_cmd", required=True)

    sub_theme_init = theme_sub.add_parser(
        "init", help="Scaffold Tailwind config and copy Greeble Tailwind preset into the project"
    )
    sub_theme_init.add_argument(
        "--project",
        default=Path.cwd(),
        type=Path,
        help="Destination project root (default: current directory)",
    )
    sub_theme_init.add_argument(
        "--config",
        default=Path("tailwind.config.cjs"),
        type=Path,
        help="Tailwind config path relative to project (default: tailwind.config.cjs)",
    )
    sub_theme_init.add_argument(
        "--preset-dest",
        default=Path("tools/greeble/tailwind/preset.cjs"),
        type=Path,
        help="Where to copy the Greeble Tailwind preset (default: tools/greeble/tailwind/preset.cjs)",
    )
    sub_theme_init.add_argument(
        "--content",
        action="append",
        default=["./templates/**/*.html", "./docs/**/*.md"],
        help="Content globs for Tailwind to scan (can be repeated)",
    )
    sub_theme_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing preset/config files if they already exist",
    )
    sub_theme_init.set_defaults(func=cmd_theme_init)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        manifest = _load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return args.func(args, manifest)


def cmd_theme_init(args: argparse.Namespace, manifest: Manifest) -> int:
    """Copy the Greeble Tailwind preset and scaffold a tailwind.config.cjs.

    - Copies packages/greeble_tailwind_preset/preset.cjs to <project>/<preset-dest>
    - Writes a tailwind.config.cjs that consumes the preset and provided content globs
    """
    project_root: Path = Path(args.project).resolve()
    config_rel: Path = Path(args.config)
    preset_rel: Path = Path(args.preset_dest)
    content_globs: list[str] = list(args.content or [])

    # Locate the preset source in the repo
    preset_dir = manifest.root / "packages" / "greeble_tailwind_preset"
    preset_src = preset_dir / "preset.cjs"
    if not preset_src.exists():
        print(
            f"error: preset source not found at {preset_src}. Ensure the repository includes packages/greeble_tailwind_preset/preset.cjs",
            file=sys.stderr,
        )
        return 2

    # Compute destinations
    preset_dest = project_root / preset_rel
    config_path = project_root / config_rel

    # Prepare bundle of preset files to copy alongside preset.cjs
    preset_targets: dict[Path, Path] = {
        preset_src: preset_dest,
    }
    theme_src = preset_dir / "theme.cjs"
    if theme_src.exists():
        preset_targets[theme_src] = preset_dest.parent / "theme.cjs"
    index_js_src = preset_dir / "index.js"
    if index_js_src.exists():
        preset_targets[index_js_src] = preset_dest.parent / "index.js"

    # Create parent directories and handle overwrite checks
    for dest in preset_targets.values():
        dest.parent.mkdir(parents=True, exist_ok=True)

    existing = [dest for dest in preset_targets.values() if dest.exists()]
    if existing and not args.force:
        paths = "\n  - ".join(str(p) for p in existing)
        print(
            "error: the following preset files already exist:\n  - "
            + paths
            + "\nRe-run with --force to overwrite",
            file=sys.stderr,
        )
        return 2

    for src, dest in preset_targets.items():
        if dest.exists() and args.force:
            print(f"Warning: Overwriting existing preset asset at {dest}", file=sys.stderr)
        dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    # Generate tailwind configuration
    # Use POSIX-style path for require()
    require_path = f"./{preset_rel.as_posix()}"
    content_lines = ",\n    ".join(f"'{g}'" for g in content_globs)
    config_js = (
        "/** Generated by greeble theme init */\n"  # header
        "module.exports = {\n"
        f"  presets: [require('{require_path}')],\n"
        "  content: [\n"
        f"    {content_lines}\n"
        "  ]\n"
        "};\n"
    )
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        if not args.force:
            print(
                f"error: config already exists at {config_path}. Re-run with --force to overwrite",
                file=sys.stderr,
            )
            return 2
        print(f"Warning: Overwriting existing config at {config_path}", file=sys.stderr)
    config_path.write_text(config_js, encoding="utf-8")

    # Print summary
    rel_config = config_path.relative_to(project_root)
    copied = sorted({path.relative_to(project_root) for path in preset_targets.values()})
    print("Scaffolded Tailwind configuration:")
    for rel in copied:
        print(f"  - Copied preset asset: {rel}")
    print(f"  - Wrote config:     {rel_config}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
