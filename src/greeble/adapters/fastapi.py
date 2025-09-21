"""
FastAPI adapter helpers for HTMX-aware server-rendered apps.

Purpose:
    Provide ergonomic utilities to:
    - Detect HTMX requests.
    - Attach HX-Trigger headers.
    - Return HTML partials.
    - Decide between full layout vs partial templates based on HX-Request.

Inputs:
    - FastAPI/Starlette Request object.
    - Jinja2Templates instance and template names.
    - Optional trigger events (string, list, or dict) to be emitted to the client.

Outputs:
    - HTMLResponse or TemplateResponse objects with appropriate headers set.

Dependencies:
    - fastapi
    - starlette (transitively via fastapi)
    - jinja2

Notes:
    These helpers do not enforce project structure; they aim to make HTMX flows explicit
    and predictable while staying framework-idiomatic.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, MutableMapping
from typing import Any, Literal

from fastapi import Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

HX_REQUEST_HEADER = "HX-Request"


def is_hx_request(request: Request) -> bool:
    """Return True if the incoming request was initiated by HTMX.

    HTMX sends the header `HX-Request: true` on requests it initiates.
    """
    # Per HTMX docs, header value is the string "true" when present
    return request.headers.get(HX_REQUEST_HEADER, "").lower() == "true"


AfterPhase = Literal["receive", "settle", "swap"]
_HEADER_BY_PHASE: dict[AfterPhase, str] = {
    "receive": "HX-Trigger",
    "settle": "HX-Trigger-After-Settle",
    "swap": "HX-Trigger-After-Swap",
}


def _serialize_triggers(triggers: str | list[str] | Mapping[str, Any]) -> str:
    """Serialize trigger spec into a JSON string for HX-Trigger headers.

    Accepts a single event name, a list of event names, or a mapping of
    event -> payload. The header value must be JSON per HTMX conventions.
    """
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
    """Build HX-Trigger* headers for the given trigger spec.

    - triggers: event name, list of names, or mapping of name->payload
    - after: when to dispatch events ("receive" -> immediate, "settle", or "swap")
    """
    header_name = _HEADER_BY_PHASE[after]
    return {header_name: _serialize_triggers(triggers)}


def partial_html(
    html: str,
    *,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> HTMLResponse:
    """Return an HTML fragment response with optional HX-Trigger headers.

    - html: the HTML fragment to return
    - status_code: HTTP status code (default 200)
    - headers: additional headers to include
    - triggers: event(s) to trigger on the client (HX-Trigger*)
    """
    hdrs: dict[str, str] = {}
    if headers:
        hdrs.update(headers)
    if triggers is not None:
        hdrs.update(hx_trigger_headers(triggers))
    return HTMLResponse(content=html, status_code=status_code, headers=hdrs)


def template_response(
    templates: Jinja2Templates,
    template_name: str,
    context: dict[str, Any],
    request: Request,
    *,
    partial: bool | None = None,
    partial_template: str | None = None,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> Response:
    """Render a template, switching to a partial when HTMX requests are detected.

    Args:
        templates: Jinja2Templates bound to your templates directory.
        template_name: Full-page layout template.
        context: Variables for the template. `request` will be injected automatically
                 as required by Starlette templates.
        request: Incoming request (used for HTMX detection and template rendering).
        partial: Force partial rendering (overrides HTMX detection) when True; when
                 False forces full layout; when None (default) auto-detect.
        partial_template: Name of the partial template to use when rendering a fragment.
        status_code: Response status code.
        headers: Additional headers to include.
        triggers: Optional trigger spec for HX-Trigger* headers.

    Behavior:
        - If `partial is True` or (`partial is None` and is_hx_request(request)) and
          `partial_template` is provided, render the partial.
        - Otherwise render the full `template_name`.
        - If `triggers` is provided, attach HX-Trigger headers.
    """
    # Ensure the Request object is present in the template context
    ctx = dict(context)
    ctx.setdefault("request", request)

    use_partial = partial is True or (partial is None and is_hx_request(request))
    name = partial_template if (use_partial and partial_template) else template_name

    resp = templates.TemplateResponse(name, ctx, status_code=status_code)

    if headers:
        for k, v in headers.items():
            resp.headers[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp.headers[k] = v

    return resp
