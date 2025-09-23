from __future__ import annotations

import shutil
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .manifest import Component, Manifest


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
    raise ScaffoldError(f"Unsupported file path '{relative}' in component '{component.key}'")


def build_copy_plan(
    manifest: Manifest,
    component: Component,
    project_root: Path,
    templates_dir: Path,
    static_dir: Path,
    include_docs: bool,
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
            destination = project_root / rel_path
        else:
            raise ScaffoldError(
                f"Unsupported file path '{relative}' in component '{component.key}'"
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
            dest_parent.mkdir(parents=True, exist_ok=True)
        if plan.destination.exists() and not force and not dry_run:
            raise ScaffoldError(f"File already exists: {plan.destination}")
        if not dry_run:
            shutil.copy2(plan.source, plan.destination)
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
