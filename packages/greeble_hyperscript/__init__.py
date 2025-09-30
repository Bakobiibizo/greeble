from __future__ import annotations

from importlib import resources
from pathlib import Path

__all__ = ["bundle_path", "bundle_file"]

_ASSET_NAME = "assets/greeble.hyperscript"


def bundle_path() -> Path:
    """Return a `Path` to the bundled Hyperscript behaviors file."""
    with resources.as_file(resources.files(__name__).joinpath(_ASSET_NAME)) as path:
        return Path(path)


def bundle_file() -> bytes:
    """Return the bundled Hyperscript file contents as bytes."""
    return bundle_path().read_bytes()
