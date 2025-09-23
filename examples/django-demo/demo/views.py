from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from greeble.adapters import django as g_django


def home(request: HttpRequest) -> HttpResponse:
    # Render the full page; the button will fetch a partial into #panel-root
    return render(request, "index.html", {})


def panel(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {"message": "Panel loaded via HTMX"}
    return g_django.template_response(
        template_name="panel.html",  # Fallback if not an HTMX request
        partial_template="panel.partial.html",
        context=context,
        request=request,
        triggers={"greeble:toast": {"level": "info", "message": "Loaded panel"}},
    )
