from __future__ import annotations

import sys
import types
from typing import Any

import pytest

from greeble.adapters import flask as g_flask


class DummyRequest:
    def __init__(
        self, headers: dict[str, str] | None = None, environ: dict[str, str] | None = None
    ) -> None:
        self.headers = headers or {}
        self.environ = environ or {}


class SimpleResponse:
    def __init__(self, body: str, status: int) -> None:
        self.body = body
        self.status = status
        self.headers: dict[str, str] = {}


def test_is_hx_request_true_and_false() -> None:
    req_true = DummyRequest(headers={"HX-Request": "true"})
    req_false = DummyRequest(headers={"HX-Request": "false"})
    assert g_flask.is_hx_request(req_true) is True
    assert g_flask.is_hx_request(req_false) is False

    # Fallback via environ
    req_env = DummyRequest(headers={}, environ={"HTTP_HX_REQUEST": "true"})
    assert g_flask.is_hx_request(req_env) is True


def test_hx_trigger_headers_variants() -> None:
    assert g_flask.hx_trigger_headers("evt") == {"HX-Trigger": '{"evt": true}'}
    assert g_flask.hx_trigger_headers(["a", "b"]) == {"HX-Trigger": '{"a": true, "b": true}'}
    assert g_flask.hx_trigger_headers({"x": {"id": 1}}, after="swap") == {
        "HX-Trigger-After-Swap": '{"x": {"id": 1}}'
    }


def test_template_response_partial_switch_and_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    # Create a fake flask module
    render_calls: list[str] = []

    def render_template(name: str, **context: Any) -> str:
        render_calls.append(name)
        return f"TPL:{name}"

    def make_response(body: str, status: int) -> SimpleResponse:
        return SimpleResponse(body, status)

    fake_flask = types.ModuleType("flask")
    fake_flask.render_template = render_template  # type: ignore[attr-defined]
    fake_flask.make_response = make_response  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, "flask", fake_flask)

    req = DummyRequest(headers={"HX-Request": "true"})
    resp = g_flask.template_response(
        template_name="full.html",
        partial_template="partial.html",
        context={"x": 1},
        request=req,
        triggers={"evt": True},
    )

    assert isinstance(resp, SimpleResponse)
    # Confirm partial chosen due to HX header
    assert render_calls == ["partial.html"]
    # Confirm HX-Trigger header attached
    assert "HX-Trigger" in resp.headers
