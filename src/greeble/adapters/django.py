"""
Django adapter helpers for HTMX-aware server-rendered apps.

These helpers mirror the FastAPI adapter semantics while using Django's
rendering and response facilities. Imports are performed inside functions
to avoid requiring Django at import time in environments that don't use it.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, MutableMapping
from typing import Any, Literal

HX_REQUEST_HEADER = "HX-Request"


def is_hx_request(request: Any) -> bool:
    """Return True if the incoming request was initiated by HTMX.

    Works with `django.http.HttpRequest` objects. HTMX sends header `HX-Request: true`.
    """
    # Django >= 2.2 exposes a case-insensitive mapping at request.headers; fallback to META
    value: Any = ""
    headers = getattr(request, "headers", None)
    if headers is not None:
        try:
            value = headers.get(HX_REQUEST_HEADER, "")
        except Exception:
            value = ""
    if not value:
        meta = getattr(request, "META", None)
        if isinstance(meta, dict):
            value = meta.get(f"HTTP_{HX_REQUEST_HEADER.replace('-', '_').upper()}", "")
    return str(value).lower() == "true"


AfterPhase = Literal["receive", "settle", "swap"]
_HEADER_BY_PHASE: dict[AfterPhase, str] = {
    "receive": "HX-Trigger",
    "settle": "HX-Trigger-After-Settle",
    "swap": "HX-Trigger-After-Swap",
}


def _serialize_triggers(triggers: str | list[str] | Mapping[str, Any]) -> str:
    if isinstance(triggers, str):
        return json.dumps({triggers: True})
    if isinstance(triggers, list):
        return json.dumps({name: True for name in triggers})
    return json.dumps(dict(triggers))


def hx_trigger_headers(
    triggers: str | list[str] | Mapping[str, Any], *, after: AfterPhase = "receive"
) -> dict[str, str]:
    header_name = _HEADER_BY_PHASE[after]
    return {header_name: _serialize_triggers(triggers)}


def partial_html(
    html: str,
    *,
    status_code: int = 200,
    headers: MutableMapping[str, str] | None = None,
    triggers: str | list[str] | Mapping[str, Any] | None = None,
) -> Any:
    """Return a Django HttpResponse with HTML content and optional HX headers."""
    from django.http import HttpResponse  # local import to avoid hard dependency at import time

    resp = HttpResponse(html, status=status_code, content_type="text/html; charset=utf-8")
    if headers:
        for k, v in headers.items():
            resp[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp[k] = v
    return resp


def csrf_header(request: Any) -> dict[str, str]:
    """Return a header mapping for CSRF suitable for HTMX requests.

    Uses Django's CSRF token API. Intended for use with hx-headers, e.g.:

        hx-headers='{"X-CSRFToken": "<token>"}'
    """
    try:
        from django.middleware.csrf import get_token
    except Exception:  # pragma: no cover - import guard for non-Django envs
        return {}
    token = get_token(request)
    return {"X-CSRFToken": token}


def hx_headers_attr(headers: Mapping[str, str]) -> str:
    """Serialize headers for use in an hx-headers attribute."""
    return json.dumps(dict(headers))


essential_context_keys = {"request"}


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
    """Render a template or partial based on HTMX detection, returning HttpResponse.

    - template_name: full layout template
    - partial_template: fragment template to use when HTMX or `partial=True`
    - request: django HttpRequest for HTMX detection and template rendering
    """
    from django.shortcuts import render

    use_partial = partial is True or (partial is None and is_hx_request(request))
    name = partial_template if (use_partial and partial_template) else template_name
    # Django's render ensures the response carries proper content type
    resp = render(request, name, context=context, status=status_code)
    if headers:
        for k, v in headers.items():
            resp[k] = v
    if triggers is not None:
        for k, v in hx_trigger_headers(triggers).items():
            resp[k] = v
    return resp
