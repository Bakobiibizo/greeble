"""Django template tags for Greeble.

Usage:
    {% load greeble_tags %}
    {% greeble_toast_container %}
    <form hx-post="/submit" hx-headers='{% greeble_csrf_headers %}'>...</form>
    <button hx-headers='{{ {"X-My-Header": "1"}|hx_headers|safe }}'>Click</button>
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django import template
from django.utils.safestring import mark_safe

from ..csrf import csrf_headers_json, serialize_headers
from ..pagination import Pagination, pagination_context
from django.middleware.csrf import get_token

register = template.Library()


@register.simple_tag
def greeble_toast_container() -> str:
    """Emit the Greeble toast region container."""
    html = (
        '<div id="greeble-toasts" class="greeble-toast-region" '
        'aria-live="polite" aria-label="Notifications"></div>'
    )
    return mark_safe(html)


@register.simple_tag(takes_context=True)
def greeble_csrf_headers(context: template.Context) -> str:
    """Return a JSON string for `hx-headers` carrying the CSRF token."""

    request = context.get("request")
    if request is None:
        return "{}"
    return csrf_headers_json(request)


@register.filter(name="hx_headers")
def hx_headers(headers: Mapping[str, Any] | None) -> str:
    """Serialize a mapping to a JSON string for `hx-headers` usage."""

    return serialize_headers(headers)


@register.simple_tag(takes_context=True)
def greeble_pagination_context(
    context: template.Context,
    pagination: Pagination,
    *,
    base_url: str | None = None,
    query_params: Mapping[str, Any] | None = None,
    page_param: str = "page",
    window: int = 2,
) -> dict[str, Any]:
    """Return a pagination context suitable for rendering Greeble controls."""

    request = context.get("request")
    if base_url is None:
        if request is None:
            raise ValueError("base_url is required when no request is present in the context")
        base_url = request.path

    params: dict[str, Any]
    if query_params is not None:
        params = dict(query_params)
    elif request is not None:
        params = {k: request.GET.get(k) for k in request.GET}
    else:
        params = {}

    return pagination_context(
        pagination,
        base_url=base_url,
        query_params=params,
        page_param=page_param,
        window=window,
    )
