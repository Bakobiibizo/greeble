from __future__ import annotations

import itertools
import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .manifest import Component, Manifest

__all__ = [
    "CopyPlan",
    "ScaffoldError",
    "backup_existing_files",
    "build_copy_plan",
    "component_sources",
    "ensure_within_project",
    "execute_plan",
    "remove_files",
]


@dataclass(frozen=True)
class CopyPlan:
    source: Path
    destination: Path


class ScaffoldError(RuntimeError):
    """Raised when scaffolding cannot complete."""


def _component_root(manifest: Manifest, component: Component) -> Path:
    return manifest.root / "packages" / "greeble_components" / "components" / component.key


def _resolve_source(manifest: Manifest, component: Component, relative: Path) -> Path:
    first = relative.parts[0]
    if first == "templates":
        return _component_root(manifest, component) / "templates" / relative.name
    if first == "static":
        return _component_root(manifest, component) / "static" / relative.name
    if first == "docs":
        return manifest.root / relative
    allowed = ", ".join(sorted({"templates", "static", "docs"}))
    raise ScaffoldError(
        f"Unsupported file path '{relative}' in component '{component.key}'. "
        f"Expected path to start with one of: {allowed}."
    )


def build_copy_plan(
    manifest: Manifest,
    component: Component,
    project_root: Path,
    templates_dir: Path,
    static_dir: Path,
    include_docs: bool,
    docs_dir: Path | None,
) -> list[CopyPlan]:
    plans: list[CopyPlan] = []

    for relative in component.files:
        rel_path = Path(relative)
        first = rel_path.parts[0]
        if first == "templates":
            source = _resolve_source(manifest, component, rel_path)
            destination = project_root / templates_dir / Path(*rel_path.parts[1:])
        elif first == "static":
            source = _resolve_source(manifest, component, rel_path)
            destination = project_root / static_dir / Path(*rel_path.parts[1:])
        elif first == "docs":
            if not include_docs:
                continue
            source = _resolve_source(manifest, component, rel_path)
            if docs_dir is not None:
                destination = project_root / docs_dir / Path(*rel_path.parts[1:])
            else:
                destination = project_root / rel_path
        else:
            raise ScaffoldError(
                f"Unsupported manifest path '{relative}' in component '{component.key}'. "
                "Paths must begin with templates/, static/, or docs/."
            )

        if not source.exists():
            raise ScaffoldError(f"Source file missing: {source}")
        plans.append(CopyPlan(source=source, destination=destination))

    return plans


def ensure_within_project(project_root: Path, destinations: Iterable[CopyPlan]) -> None:
    project_root = project_root.resolve()
    for plan in destinations:
        dest = plan.destination.resolve()
        if project_root not in dest.parents and dest != project_root:
            raise ScaffoldError(f"Refusing to write outside project root: {dest}")


def execute_plan(plans: Iterable[CopyPlan], *, force: bool, dry_run: bool) -> list[Path]:
    written: list[Path] = []
    for plan in plans:
        if not dry_run:
            dest_parent = plan.destination.parent
            try:
                dest_parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ScaffoldError(
                    f"Failed to create destination directory '{dest_parent}': {e}"
                ) from e
        if plan.destination.exists() and not force and not dry_run:
            raise ScaffoldError(f"File already exists: {plan.destination}")
        if not dry_run:
            try:
                shutil.copy2(plan.source, plan.destination)
            except OSError as e:
                raise ScaffoldError(f"Failed to copy to '{plan.destination}': {e}") from e
        written.append(plan.destination)
    return written


def remove_files(plans: Iterable[CopyPlan], *, dry_run: bool) -> tuple[list[Path], list[Path]]:
    removed: list[Path] = []
    missing: list[Path] = []
    for plan in plans:
        if plan.destination.exists():
            if not dry_run:
                plan.destination.unlink()
            removed.append(plan.destination)
        else:
            missing.append(plan.destination)
    return removed, missing


def component_sources(manifest: Manifest, component: Component) -> list[Path]:
    sources: list[Path] = []
    for relative in component.files:
        rel_path = Path(relative)
        sources.append(_resolve_source(manifest, component, rel_path))
    return sources


def _next_backup_path(path: Path, suffix: str = ".bak") -> Path:
    candidate = path.with_name(path.name + suffix)
    if not candidate.exists():
        return candidate
    for index in itertools.count(1):
        numbered = path.with_name(f"{path.name}{suffix}{index}")
        if not numbered.exists():
            return numbered
    raise ScaffoldError(f"Unable to determine backup path for {path}")


def backup_existing_files(plans: Iterable[CopyPlan], *, suffix: str = ".bak") -> list[Path]:
    backups: list[Path] = []
    for plan in plans:
        destination = plan.destination
        if not destination.exists():
            continue
        backup_path = _next_backup_path(destination, suffix=suffix)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(destination, backup_path)
        backups.append(backup_path)
    return backups
