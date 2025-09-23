"""
Flask adapter helpers for HTMX-aware server-rendered apps.

These helpers mirror the FastAPI adapter semantics while using Flask's
rendering and response facilities. Imports are performed inside functions
to avoid requiring Flask at import time in environments that don't use it.

Security note: Prefer `template_response()` (which uses `render_template`) for
dynamic content so Jinja can safely escape values. `partial_html()` should only
be used for trusted, server-generated fragments.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any

from .utils import hx_trigger_headers, is_hx_request


def template_response(
    template_name: str,
    context: dict[str, Any],
    request: Any,
    *,
    partial: bool | None = None,
    partial_template: str | None = None,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> Any:
    """Render a template or partial based on HTMX detection, returning a Flask Response.

    - template_name: full layout template
    - partial_template: fragment template to use when HTMX or `partial=True`
    - request: flask request object for HTMX detection
    """
    from flask import make_response, render_template

    use_partial = partial is True or (partial is None and is_hx_request(request))
    name = partial_template if (use_partial and partial_template) else template_name
    html = render_template(name, **context)
    resp = make_response(html, status_code)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp.headers[k] = v
    return resp
