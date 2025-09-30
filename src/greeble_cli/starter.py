from __future__ import annotations

import contextlib
import shutil
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from .manifest import Manifest
from .scaffold import (
    build_copy_plan,
    ensure_within_project,
    execute_plan,
)

STARTER_COMPONENTS: tuple[str, ...] = (
    "button",
    "dropdown",
    "modal",
    "tabs",
    "drawer",
    "table",
    "palette",
    "form-validated",
    "stepper",
    "infinite-list",
    "toast",
)

STARTER_STATIC_FILES = {
    "static/site.css": "site.css",
    "static/logo.svg": "logo.svg",
}

HYPERSCRIPT_DEST = Path("static/greeble/hyperscript/greeble.hyperscript")

STARTER_APP_FILES = {
    "src/greeble_starter/app.py": "app_main.py",
    "src/greeble_starter/__init__.py": "package_init.py",
    "src/greeble_starter/__main__.py": "package_dunder_main.py",
}

STARTER_ROOT_FILES = {
    "README.md": "starter_README.md",
    "pyproject.toml": "starter_pyproject.toml",
}


@dataclass(frozen=True)
class StarterPlan:
    component_files: list[Path]
    project_files: list[Path]


class StarterError(RuntimeError):
    """Raised when starter scaffold fails."""


TEMPLATES_DIR = Path(__file__).resolve().parent / "templates" / "starter"
REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_IMAGES = REPO_ROOT / "public" / "images"
LANDING_STYLES_DEST = Path("static/greeble/greeble-landing.css")
HYPERSCRIPT_REPO_PATH = (
    REPO_ROOT / "packages" / "greeble_hyperscript" / "assets" / "greeble.hyperscript"
)
LOGO_SOURCE = TEMPLATES_DIR / "logo.svg"


def _write_file(destination: Path, template_name: str, *, dry_run: bool) -> None:
    source = TEMPLATES_DIR / template_name
    if not source.exists():  # pragma: no cover - defensive
        raise StarterError(f"Starter template missing: {template_name}")
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _copy_landing_styles(destination: Path, *, dry_run: bool, force: bool = False) -> None:
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)

    def copy_from(source: Path) -> bool:
        if not source.is_file():
            return False
        if destination.exists() and not force:
            raise StarterError(f"Landing stylesheet already exists: {destination}")
        shutil.copy2(source, destination)
        return True

    with contextlib.suppress(ModuleNotFoundError, FileNotFoundError):
        traversable = resources.files("greeble_core").joinpath(
            "assets", "css", "greeble-landing.css"
        )
        with resources.as_file(traversable) as path:
            if copy_from(Path(path)):
                return

    repo_candidate = (
        REPO_ROOT / "packages" / "greeble_core" / "assets" / "css" / "greeble-landing.css"
    )
    if copy_from(repo_candidate):
        return

    raise StarterError("Landing stylesheet could not be located in greeble_core assets")


def _copy_hyperscript_bundle(destination: Path, *, dry_run: bool, force: bool = False) -> None:
    if dry_run:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)

    def copy_from(source: Path) -> bool:
        if not source.is_file():
            return False
        if destination.exists() and not force:
            raise StarterError(f"Hyperscript bundle already exists: {destination}")
        shutil.copy2(source, destination)
        return True

    with contextlib.suppress(ModuleNotFoundError, FileNotFoundError):
        traversable = resources.files("greeble_hyperscript").joinpath(
            "assets", "greeble.hyperscript"
        )
        with resources.as_file(traversable) as path:
            if copy_from(Path(path)):
                return

    if copy_from(HYPERSCRIPT_REPO_PATH):
        return

    raise StarterError("Hyperscript bundle could not be located in greeble_hyperscript assets")


def scaffold_starter(
    *,
    manifest: Manifest,
    project_root: Path,
    include_docs: bool,
    docs_dir: Path,
    force: bool,
    dry_run: bool,
) -> StarterPlan:
    project_root = project_root.resolve()
    component_plans: list[Path] = []
    for key in STARTER_COMPONENTS:
        component = manifest.get(key)
        plans = build_copy_plan(
            manifest=manifest,
            component=component,
            project_root=project_root,
            templates_dir=Path("templates"),
            static_dir=Path("static"),
            include_docs=include_docs,
            docs_dir=docs_dir,
        )
        ensure_within_project(project_root, plans)
        component_plans.extend(plan.destination for plan in plans)
        if dry_run:
            continue
        execute_plan(plans, force=force, dry_run=False)

    project_files: list[Path] = []
    for rel, template_name in STARTER_ROOT_FILES.items():
        dest = project_root / rel
        _write_file(dest, template_name, dry_run=dry_run)
        project_files.append(dest)

    for rel, template_name in STARTER_APP_FILES.items():
        dest = project_root / rel
        _write_file(dest, template_name, dry_run=dry_run)
        project_files.append(dest)

    for rel, template_name in STARTER_STATIC_FILES.items():
        dest = project_root / rel
        _write_file(dest, template_name, dry_run=dry_run)
        project_files.append(dest)

    landing_dest = project_root / LANDING_STYLES_DEST
    _copy_landing_styles(landing_dest, dry_run=dry_run, force=force)
    project_files.append(landing_dest)

    hyperscript_dest = project_root / HYPERSCRIPT_DEST
    _copy_hyperscript_bundle(hyperscript_dest, dry_run=dry_run, force=force)
    project_files.append(hyperscript_dest)

    index_dest = project_root / "templates/index.html"
    _write_file(index_dest, "index.html", dry_run=dry_run)
    project_files.append(index_dest)

    # Best-effort: copy branding icons into starter static/images for favicons
    with contextlib.suppress(Exception):  # pragma: no cover - non-fatal
        icons = [
            "greeble-icon-black.svg",
            "greeble-icon-alpha-white.png",
            "greeble-icon-alpha-black.png",
        ]
        dest_dir = project_root / "static" / "images"
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
        for name in icons:
            source = PUBLIC_IMAGES / name
            if source.exists() and not dry_run:
                shutil.copy2(source, dest_dir / name)

    component_plans_sorted = sorted(component_plans, key=lambda path: tuple(path.parts))
    project_files_sorted = sorted(project_files, key=lambda path: tuple(path.parts))
    return StarterPlan(component_files=component_plans_sorted, project_files=project_files_sorted)
