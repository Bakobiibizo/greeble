"""
Flask adapter helpers for HTMX-aware server-rendered apps.

This mirrors the FastAPI adapter API to provide a consistent developer
experience across frameworks.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, MutableMapping
from typing import Any, Literal

from flask import Response as FlaskResponse
from flask import make_response, render_template
from flask import request as flask_request

HX_REQUEST_HEADER = "HX-Request"

AfterPhase = Literal["receive", "settle", "swap"]
_HEADER_BY_PHASE: dict[AfterPhase, str] = {
    "receive": "HX-Trigger",
    "settle": "HX-Trigger-After-Settle",
    "swap": "HX-Trigger-After-Swap",
}


def is_hx_request(req: Any) -> bool:
    """Return True if the incoming request was initiated by HTMX.

    Accepts a Flask/Werkzeug Request (or any object exposing a `.headers` mapping).
    HTMX sends the header `HX-Request: true` on requests it initiates.
    """
    try:
        value = req.headers.get(HX_REQUEST_HEADER, "")
    except Exception:  # noqa: BLE001 - be permissive for duck-typing
        return False
    return str(value).lower() == "true"


def _serialize_triggers(triggers: str | list[str] | Mapping[str, Any]) -> str:
    if isinstance(triggers, str):
        return json.dumps({triggers: True})
    if isinstance(triggers, list):
        return json.dumps({name: True for name in triggers})
    # Mapping provided by caller is passed through as-is
    return json.dumps(dict(triggers))


def hx_trigger_headers(
    triggers: str | list[str] | Mapping[str, Any],
    *,
    after: AfterPhase = "receive",
) -> dict[str, str]:
    header_name = _HEADER_BY_PHASE[after]
    return {header_name: _serialize_triggers(triggers)}


def partial_html(
    html: str,
    *,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> FlaskResponse:
    """Return an HTML fragment response with optional HX-Trigger headers."""
    resp = make_response(html, status_code)
    resp.headers.setdefault("Content-Type", "text/html; charset=utf-8")
    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp.headers[k] = v
    return resp


def template_response(
    template_name: str,
    context: dict[str, Any],
    req: Any | None = None,
    *,
    partial: bool | None = None,
    partial_template: str | None = None,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> FlaskResponse:
    """Render a template, switching to a partial when HTMX requests are detected.

    Behavior:
      - If `partial is True` or (`partial is None` and is_hx_request(req or flask.request)) and
        `partial_template` is provided, render the partial.
      - Otherwise render the full `template_name`.
      - If `triggers` is provided, attach HX-Trigger headers.
    """
    # Allow omitting req and fall back to Flask's thread-local request
    if req is None:
        req = flask_request

    use_partial = partial is True or (partial is None and is_hx_request(req))
    name = partial_template if (use_partial and partial_template) else template_name

    rendered = render_template(name, **context)
    resp = make_response(rendered, status_code)
    resp.headers.setdefault("Content-Type", "text/html; charset=utf-8")

    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp.headers[k] = v

    return resp
