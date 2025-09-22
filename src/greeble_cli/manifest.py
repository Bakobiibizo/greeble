from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Component:
    """Component metadata loaded from the manifest."""

    key: str
    title: str
    summary: str
    files: list[str]


@dataclass(frozen=True)
class Manifest:
    version: int
    components: dict[str, Component]
    root: Path
    library: dict[str, object]

    def get(self, key: str) -> Component:
        try:
            return self.components[key]
        except KeyError as exc:  # pragma: no cover - defensive path
            available = ", ".join(sorted(self.components))
            raise KeyError(f"Unknown component '{key}'. Available: {available}") from exc

    def keys(self) -> Iterable[str]:
        return self.components.keys()

    @property
    def tokens_file(self) -> Path | None:
        value = self.library.get("tokens_file")
        if isinstance(value, str):
            return (self.root / value).resolve()
        return None


class ManifestError(RuntimeError):
    """Raised when the manifest cannot be parsed."""


def load_manifest(path: Path) -> Manifest:
    if not path.exists():
        raise ManifestError(f"Manifest file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestError("Manifest root must be a mapping")

    version = data.get("version")
    if not isinstance(version, int):
        raise ManifestError("Manifest 'version' must be an integer")

    raw_components = data.get("components")
    if not isinstance(raw_components, list):
        raise ManifestError("Manifest 'components' must be a list")

    components: dict[str, Component] = {}
    for entry in raw_components:
        if not isinstance(entry, dict):
            raise ManifestError("Each component entry must be a mapping")
        key = entry.get("key")
        if not isinstance(key, str):
            raise ManifestError("Component entry missing string 'key'")
        title = entry.get("title", key.title())
        summary = entry.get("summary", "")
        files = entry.get("files", [])
        if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
            raise ManifestError(f"Component '{key}' has invalid 'files' list")
        components[key] = Component(key=key, title=title, summary=summary, files=list(files))

    library = data.get("library")
    library_data: dict[str, object] = library if isinstance(library, dict) else {}

    return Manifest(
        version=version,
        components=components,
        root=path.parent,
        library=library_data,
    )


def default_manifest_path() -> Path:
    return Path(__file__).resolve().parents[2] / "greeble.manifest.yaml"
