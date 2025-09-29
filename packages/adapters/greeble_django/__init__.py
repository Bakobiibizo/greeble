"""Public entry points for the :mod:`greeble_django` adapter package.

The adapter collects helper utilities that make it easier to consume Greeble's
HTML-first components within Django projects. Everything is designed to be
HTMX-aware, mirroring the FastAPI helpers shipped in :mod:`greeble.adapters`.

Exported helpers:

* :func:`csrf_header` – return a mapping suitable for ``hx-headers`` so HTMX
  requests include a CSRF token.
* :func:`csrf_headers_json` – JSON representation of :func:`csrf_header` for
  inline attribute usage.
* :func:`serialize_headers` – utility to encode arbitrary header mappings for
  HTMX consumption.
* :class:`GreebleMessagesToToastsMiddleware` – translate Django flash messages
  into ``HX-Trigger`` payloads that drive the Greeble toast container.
* Pagination helpers (``paginate_sequence``, ``build_pagination_links``, and
  ``pagination_context``) – ergonomics for creating the context expected by the
  table component's paginator.

Template tags live in ``templatetags/greeble_tags.py`` and are discovered by
Django automatically when the app is installed.
"""

from __future__ import annotations

from .csrf import csrf_header, csrf_headers_json, serialize_headers
from .middleware import GreebleMessagesToToastsMiddleware
from .pagination import (
    PageLink,
    Pagination,
    build_pagination_links,
    paginate_sequence,
    pagination_context,
)

__all__ = [
    "csrf_header",
    "csrf_headers_json",
    "serialize_headers",
    "GreebleMessagesToToastsMiddleware",
    "paginate_sequence",
    "pagination_context",
    "build_pagination_links",
    "Pagination",
    "PageLink",
]
