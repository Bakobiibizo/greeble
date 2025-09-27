"""Django template tags for Greeble.

Usage:
    {% load greeble_tags %}
    {% greeble_toast_container %}
    <form hx-post="/submit" hx-headers='{% greeble_csrf_headers %}'>...</form>
    <button hx-headers='{{ {"X-My-Header": "1"}|hx_headers|safe }}'>Click</button>
"""

from __future__ import annotations

import json
from typing import Any

from django import template
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe

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
    """Return a JSON string for hx-headers carrying the CSRF token."""
    request = context.get("request")
    if request is None:
        return "{}"
    token = get_token(request)
    return json.dumps({"X-CSRFToken": token})


@register.filter(name="hx_headers")
def hx_headers(headers: dict[str, Any] | None) -> str:
    """Serialize a dict to a JSON string for hx-headers usage."""
    return json.dumps(headers or {})
