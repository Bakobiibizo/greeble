from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .manifest import Component, Manifest, ManifestError, default_manifest_path, load_manifest
from .scaffold import (
    CopyPlan,
    ScaffoldError,
    build_copy_plan,
    component_sources,
    ensure_within_project,
    execute_plan,
    remove_files,
)
from .starter import StarterError, scaffold_starter


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


def cmd_list(args: argparse.Namespace, manifest: Manifest) -> int:  # noqa: ARG001
    print("Available components:\n")
    for key in sorted(manifest.keys()):
        component = manifest.get(key)
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
        written = _copy_component(
            manifest=manifest,
            component=component,
            project_root=project_root,
            templates=templates_dir,
            static=static_dir,
            docs=docs_dir,
            include_docs=args.include_docs,
            force=True,
            dry_run=args.dry_run,
        )
    except ScaffoldError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        return 0

    print(f"Synced {len(written)} file(s).")
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
        templates_dir = project_root / Path(args.templates)
        static_dir = project_root / Path(args.static)
        docs_dir = project_root / Path(args.docs) if args.include_docs else None
        _print_project_status(project_root, templates_dir, static_dir, docs_dir)

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
    sub_doctor.set_defaults(func=cmd_doctor)

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


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
