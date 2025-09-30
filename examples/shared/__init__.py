from __future__ import annotations

from .assets import (
    apply_fastapi_assets,
    apply_flask_assets,
    asset_mounts,
    django_static_dirs,
    head_markup,
    public_images_path,
)

__all__ = [
    "apply_fastapi_assets",
    "apply_flask_assets",
    "asset_mounts",
    "django_static_dirs",
    "head_markup",
    "public_images_path",
]
