from __future__ import annotations

import sys
import types
from typing import Any

import pytest

from greeble.adapters import django as g_django


class DummyRequest:
    def __init__(
        self, headers: dict[str, str] | None = None, meta: dict[str, str] | None = None
    ) -> None:
        self.headers = headers or {}
        self.META = meta or {}


class SimpleHttpResponse:
    def __init__(self, content: str, status: int, content_type: str) -> None:
        self.content = content
        self.status_code = status
        self.content_type = content_type
        self._headers: dict[str, str] = {}

    # Django HttpResponse supports item assignment for headers
    def __setitem__(self, key: str, value: str) -> None:  # pragma: no cover - simple setter
        self._headers[key] = value

    @property
    def headers(self) -> dict[str, str]:  # convenience in tests
        return self._headers


def test_is_hx_request_true_false_and_meta() -> None:
    req_true = DummyRequest(headers={"HX-Request": "true"})
    req_false = DummyRequest(headers={"HX-Request": "false"})
    assert g_django.is_hx_request(req_true) is True
    assert g_django.is_hx_request(req_false) is False

    # Fallback to META
    req_meta = DummyRequest(meta={"HTTP_HX_REQUEST": "true"})
    assert g_django.is_hx_request(req_meta) is True


def test_hx_trigger_headers_variants() -> None:
    assert g_django.hx_trigger_headers("evt") == {"HX-Trigger": '{"evt": true}'}
    assert g_django.hx_trigger_headers(["a", "b"]) == {"HX-Trigger": '{"a": true, "b": true}'}
    assert g_django.hx_trigger_headers({"x": {"id": 1}}, after="settle") == {
        "HX-Trigger-After-Settle": '{"x": {"id": 1}}'
    }


def test_template_response_and_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    # Fake django.http.HttpResponse
    fake_http = types.ModuleType("django.http")

    def HttpResponse(content: str, status: int, content_type: str) -> SimpleHttpResponse:  # noqa: N802
        return SimpleHttpResponse(content, status, content_type)

    fake_http.HttpResponse = HttpResponse  # type: ignore[attr-defined]

    # Fake django.shortcuts.render
    render_calls: list[tuple[str, dict[str, Any]]] = []
    fake_shortcuts = types.ModuleType("django.shortcuts")

    def render(
        request: Any, template_name: str, *, context: dict[str, Any], status: int
    ) -> SimpleHttpResponse:
        render_calls.append((template_name, context))
        return SimpleHttpResponse(f"TPL:{template_name}", status, "text/html; charset=utf-8")

    fake_shortcuts.render = render  # type: ignore[attr-defined]

    # Register the parent package and submodules
    fake_django = types.ModuleType("django")
    monkeypatch.setitem(sys.modules, "django", fake_django)
    monkeypatch.setitem(sys.modules, "django.http", fake_http)
    monkeypatch.setitem(sys.modules, "django.shortcuts", fake_shortcuts)

    # template_response should pick partial when HX request and attach headers
    req = DummyRequest(headers={"HX-Request": "true"})
    resp2 = g_django.template_response(
        template_name="full.html",
        partial_template="partial.html",
        context={"x": 1},
        request=req,
        triggers={"evt": True},
    )
    assert isinstance(resp2, SimpleHttpResponse)
    assert render_calls and render_calls[0][0] == "partial.html"
    # Header set on response
    assert resp2.headers.get("HX-Trigger") == '{"evt": true}'
