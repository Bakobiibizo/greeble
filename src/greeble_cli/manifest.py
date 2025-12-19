from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from importlib import metadata
from importlib import resources
from pathlib import Path

import yaml

__all__ = [
    "Component",
    "Manifest",
    "ManifestError",
    "default_manifest_path",
    "load_manifest",
]


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
    path: Path

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
        return (self.root / value).resolve() if isinstance(value, str) else None


class ManifestError(RuntimeError):
    """Raised when the manifest cannot be parsed."""


ALLOWED_ROOT_KEYS = {"version", "components", "library"}
ALLOWED_COMPONENT_KEYS = {
    "key",
    "title",
    "summary",
    "files",
    "endpoints",
    "events",
    "accessibility",
}
ALLOWED_FILE_PREFIXES = {"templates", "static", "docs"}


def _validate_component_files(key: str, files: Iterable[str]) -> None:
    for file_path in files:
        if not isinstance(file_path, str) or not file_path.strip():
            raise ManifestError(f"Component '{key}' has an empty file path entry")
        rel = Path(file_path)
        if rel.is_absolute():
            raise ManifestError(
                f"Component '{key}' file '{file_path}' must be relative (no leading /)"
            )
        parts = rel.parts
        if not parts or parts[0] not in ALLOWED_FILE_PREFIXES:
            allowed = ", ".join(sorted(ALLOWED_FILE_PREFIXES))
            raise ManifestError(
                f"Component '{key}' file '{file_path}' must start with one of: {allowed}"
            )
        if len(parts) < 2:
            raise ManifestError(
                f"Component '{key}' file '{file_path}' is missing the target filename"
            )


def load_manifest(path: Path) -> Manifest:
    if not path.exists():
        raise ManifestError(f"Manifest file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestError("Manifest root must be a mapping")

    unknown_root = set(data) - ALLOWED_ROOT_KEYS
    if unknown_root:
        raise ManifestError(
            f"Manifest contains unknown top-level keys: {', '.join(sorted(unknown_root))}"
        )

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
        unknown_component_keys = set(entry) - ALLOWED_COMPONENT_KEYS
        if unknown_component_keys:
            raise ManifestError(
                f"Component '{key}' has unknown fields: "
                + ", ".join(sorted(unknown_component_keys))
            )
        if key in components:
            raise ManifestError(f"Duplicate component key '{key}'")
        title = entry.get("title", key.title())
        summary = entry.get("summary", "")
        files = entry.get("files", [])
        if not isinstance(files, list) or not all(isinstance(p, str) for p in files):
            raise ManifestError(f"Component '{key}' has invalid 'files' list")
        _validate_component_files(key, files)
        components[key] = Component(key=key, title=title, summary=summary, files=list(files))

    library = data.get("library")
    allowed_library_keys = {"packages", "tokens_file", "name", "description", "docs_site"}
    if library is None:
        library_data: dict[str, object] = {}
    elif isinstance(library, dict):
        library_data = dict(library)
        unknown_keys = set(library_data) - allowed_library_keys
        if unknown_keys:
            raise ManifestError(
                "Manifest 'library' contains unknown keys: " + ", ".join(sorted(unknown_keys))
            )
    else:
        raise ManifestError("Manifest 'library' must be a mapping when provided")

    packages = library_data.get("packages")
    if packages is not None and (
        not isinstance(packages, list) or not all(isinstance(pkg, str) for pkg in packages)
    ):
        raise ManifestError("library.packages must be a list of strings when provided")
    tokens_file = library_data.get("tokens_file")
    if tokens_file is not None and not isinstance(tokens_file, str):
        raise ManifestError("library.tokens_file must be a string when provided")

    return Manifest(
        version=version,
        components=components,
        root=path.parent,
        library=library_data,
        path=path,
    )


def default_manifest_path() -> Path:
    manifest_name = "greeble.manifest.yaml"

    try:
        packaged = resources.files("greeble_cli").joinpath(manifest_name)
    except Exception:
        packaged = None
    else:
        try:
            packaged_path = Path(packaged)
        except TypeError:
            packaged_path = None
        else:
            if packaged_path.exists():
                return packaged_path

    try:
        dist = metadata.distribution("greeble")
    except metadata.PackageNotFoundError:
        dist = None

    if dist is not None:
        try:
            candidate = Path(dist.locate_file(manifest_name))
        except Exception:
            candidate = None
        else:
            if candidate.exists():
                return candidate

    try:
        files = metadata.files("greeble")
    except metadata.PackageNotFoundError:
        files = None

    if files:
        for file in files:
            if str(file).endswith(manifest_name):
                try:
                    return Path(file.locate())
                except Exception:
                    break

    resolved = Path(__file__).resolve()
    for parent in resolved.parents:
        candidate = parent / manifest_name
        if candidate.exists():
            return candidate

    return resolved.parents[2] / manifest_name
