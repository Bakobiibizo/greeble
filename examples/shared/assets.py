from __future__ import annotations

import textwrap
from collections.abc import Iterable, Mapping
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from flask import Flask
from markupsafe import Markup
from werkzeug.middleware.shared_data import SharedDataMiddleware

REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_ASSETS = REPO_ROOT / "packages" / "greeble_core" / "assets" / "css"
HYPERSCRIPT_ASSETS = REPO_ROOT / "packages" / "greeble_hyperscript" / "assets"
PUBLIC_IMAGES = REPO_ROOT / "public" / "images"

_HEAD_MARKUP = textwrap.dedent(
    """
    <link rel="stylesheet" href="/static/greeble/greeble-core.css" />
    <link rel="stylesheet" href="/static/greeble/greeble-landing.css" />
    <link rel="icon" href="/static/images/greeble-icon-black.svg" type="image/svg+xml" media="(prefers-color-scheme: light)" />
    <link rel="icon" href="/static/images/greeble-icon-alpha-white.png" sizes="any" media="(prefers-color-scheme: dark)" />
    <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/sse.js" defer></script>
    <script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
    <script type="text/hyperscript" src="/static/greeble/hyperscript/greeble.hyperscript"></script>
    """
).strip()


def asset_mounts() -> dict[str, Path]:
    """Return mapping of mount paths to asset directories."""

    return {
        "/static/greeble": CORE_ASSETS,
        "/static/greeble/hyperscript": HYPERSCRIPT_ASSETS,
        "/static/images": PUBLIC_IMAGES,
    }


_MOUNT_NAMES: Mapping[str, str] = {
    "/static/greeble": "greeble-static",
    "/static/greeble/hyperscript": "greeble-hyperscript",
    "/static/images": "greeble-images",
}


def apply_fastapi_assets(app: FastAPI) -> None:
    """Mount shared static assets on a FastAPI instance."""

    for mount, path in asset_mounts().items():
        name = _MOUNT_NAMES[mount]
        app.mount(mount, StaticFiles(directory=str(path)), name=name)


def apply_flask_assets(app: Flask) -> None:
    """Mount shared static assets on a Flask instance."""

    mounts = {mount: str(path) for mount, path in asset_mounts().items()}
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, mounts)

    @app.context_processor  # pragma: no cover - framework hook
    def _inject_greeble_assets() -> Mapping[str, str]:
        return {"greeble_head_assets": head_markup()}


def django_static_dirs() -> Iterable[tuple[str, Path]]:
    """Return static directory tuples suitable for Django's ``STATICFILES_DIRS``."""

    mounts = asset_mounts()
    return [
        ("greeble", mounts["/static/greeble"]),
        ("greeble/hyperscript", mounts["/static/greeble/hyperscript"]),
        ("images", mounts["/static/images"]),
    ]


def public_images_path() -> Path:
    """Expose the public images directory path."""

    return PUBLIC_IMAGES


def head_markup() -> Markup:
    """Return the head asset HTML marked safe for template engines."""

    return Markup(_HEAD_MARKUP)
