"""
Django adapter helpers for HTMX-aware server-rendered apps.

These helpers mirror the FastAPI adapter semantics while using Django's
rendering and response facilities. Imports are performed inside functions
to avoid requiring Django at import time in environments that don't use it.

Security note: Prefer `template_response()` (which uses Django's template engine)
for dynamic content. `partial_html()` should only be used for trusted, server-
generated fragments.
"""

import json
from collections.abc import Mapping, MutableMapping
from typing import Any

from .utils import hx_trigger_headers, is_hx_request


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
