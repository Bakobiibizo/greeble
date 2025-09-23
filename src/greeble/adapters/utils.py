from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, Literal

HX_REQUEST_HEADER = "HX-Request"
AfterPhase = Literal["receive", "settle", "swap"]
_HEADER_BY_PHASE: dict[AfterPhase, str] = {
    "receive": "HX-Trigger",
    "settle": "HX-Trigger-After-Settle",
    "swap": "HX-Trigger-After-Swap",
}


def is_hx_request(request: Any) -> bool:
    """Return True if the incoming request was initiated by HTMX (framework-agnostic).

    Attempts to read `request.headers` (Flask/Django/Starlette) and falls back to
    environ-style dicts `request.environ` (Flask) or `request.META` (Django).
    """
    value: Any = ""
    headers = getattr(request, "headers", None)
    if headers is not None:
        try:
            value = headers.get(HX_REQUEST_HEADER, "")
        except Exception:
            value = ""
    if not value:
        environ = getattr(request, "environ", None)
        if isinstance(environ, dict):
            value = environ.get(f"HTTP_{HX_REQUEST_HEADER.replace('-', '_').upper()}", "")
    if not value:
        meta = getattr(request, "META", None)
        if isinstance(meta, dict):
            value = meta.get(f"HTTP_{HX_REQUEST_HEADER.replace('-', '_').upper()}", "")
    return str(value).lower() == "true"


def serialize_triggers(triggers: str | list[str] | Mapping[str, Any]) -> str:
    if isinstance(triggers, str):
        return json.dumps({triggers: True})
    if isinstance(triggers, list):
        return json.dumps({name: True for name in triggers})
    return json.dumps(dict(triggers))


def hx_trigger_headers(
    triggers: str | list[str] | Mapping[str, Any], *, after: AfterPhase = "receive"
) -> dict[str, str]:
    header_name = _HEADER_BY_PHASE[after]
    return {header_name: serialize_triggers(triggers)}
