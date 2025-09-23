"""
Django middleware helpers for Greeble adapters.

Includes:
- GreebleMessagesToToastsMiddleware: emits HX-Trigger headers for Django messages.

This module lives under `src/greeble/adapters/` so projects can reference it via
`'greeble.adapters.middleware.GreebleMessagesToToastsMiddleware'` in MIDDLEWARE
when `'greeble.adapters'` is added to INSTALLED_APPS.
"""

from __future__ import annotations

import json
from typing import Any


class GreebleMessagesToToastsMiddleware:
    """Emit HX-Trigger headers for Django messages.

    - Collects messages via `django.contrib.messages.get_messages`.
    - If any exist and the response is HTML, attach an HX-Trigger header of the form:
        {"greeble:toast": [{"level": "info", "title": "...", "message": "..."}, ...]}

    Client code can listen for this event and render toasts into `#greeble-toasts`.
    """

    def __init__(self, get_response: Any) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:  # pragma: no cover - glue
        response = self.get_response(request)
        try:
            from django.contrib.messages import get_messages  # defer import
        except Exception:
            return response

        try:
            stored = list(get_messages(request))
        except Exception:
            return response

        if not stored:
            return response

        # Only attach on HTML responses
        ctype = getattr(response, "headers", {}).get("Content-Type") or getattr(
            response, "content_type", ""
        )
        if not isinstance(ctype, str) or "html" not in ctype:
            return response

        payload = [
            {
                "level": getattr(m, "level_tag", "info"),
                "title": getattr(m, "extra_tags", ""),
                "message": str(m),
            }
            for m in stored
        ]

        header_name = "HX-Trigger"
        body = json.dumps({"greeble:toast": payload})

        # Merge with any existing HX-Trigger header by combining JSON objects
        existing = None
        hdrs = getattr(response, "headers", None)
        if hdrs is not None:
            try:
                existing = hdrs.get(header_name)
            except Exception:
                existing = None
        if existing is None:
            existing = getattr(response, header_name, None)

        if existing:
            try:
                merged = json.loads(existing)
                if isinstance(merged, dict):
                    merged.update({"greeble:toast": payload})
                    body = json.dumps(merged)
            except Exception:
                pass

        hdrs = getattr(response, "headers", None)
        if hdrs is not None:
            try:
                hdrs[header_name] = body
                return response
            except Exception:
                pass
        try:
            response[header_name] = body
        except Exception:
            setattr(response, header_name, body)

        return response
