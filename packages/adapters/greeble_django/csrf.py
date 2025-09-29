"""Django CSRF helpers for HTMX-aware responses and templates.

These helpers wrap Django's CSRF token retrieval so that applications can easily
inject the token into `hx-headers` attributes or response headers. All imports
are local to keep the module importable in environments without Django.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

__all__ = ["csrf_header", "csrf_headers_json", "serialize_headers"]


def csrf_header(request: Any) -> dict[str, str]:
    """Return a mapping containing the current CSRF token for ``hx-headers``.

    The helper mirrors the FastAPI adapter's `csrf_header` behaviour but guards
    against Django being absent at runtime (e.g. when included in a starter that
    hasn't installed Django yet). Missing imports or token failures yield an
    empty mapping so callers can safely merge the result.
    """

    try:
        from django.middleware.csrf import get_token
    except Exception:  # pragma: no cover - keeps module importable without Django
        return {}

    try:
        token = get_token(request)
    except Exception:
        return {}

    return {"X-CSRFToken": token}


def csrf_headers_json(request: Any) -> str:
    """Return a JSON representation of :func:`csrf_header` for inline use."""

    return json.dumps(csrf_header(request))


def serialize_headers(headers: Mapping[str, Any] | None) -> str:
    """Serialize an arbitrary mapping to the JSON string HTMX expects.

    ``hx-headers`` accepts JSON; this helper ensures non-serializable values
    raise predictable ``TypeError`` exceptions rather than silently failing.
    """

    if headers is None:
        return "{}"
    return json.dumps(dict(headers))
