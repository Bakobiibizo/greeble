from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.testclient import TestClient
from starlette.types import Scope

from greeble.adapters.fastapi import (
    HX_REQUEST_HEADER,
    hx_trigger_headers,
    is_hx_request,
    partial_html,
    template_response,
)


def make_request(headers: dict[str, str] | None = None) -> Request:
    # Minimal ASGI scope for Request
    hdrs = []
    if headers:
        hdrs = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    scope: Scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "headers": hdrs,
        "query_string": b"",
        "client": ("test", 12345),
        "server": ("testserver", 80),
        "scheme": "http",
    }
    return Request(scope)


def test_is_hx_request_true_false() -> None:
    assert is_hx_request(make_request({HX_REQUEST_HEADER: "true"})) is True
    assert is_hx_request(make_request({HX_REQUEST_HEADER: "TRUE"})) is True
    assert is_hx_request(make_request({HX_REQUEST_HEADER: "false"})) is False
    assert is_hx_request(make_request({})) is False


def test_hx_trigger_headers_serialization() -> None:
    # single string
    h1 = hx_trigger_headers("greeble:ok")
    assert json.loads(h1["HX-Trigger"]) == {"greeble:ok": True}

    # list of strings
    h2 = hx_trigger_headers(["one", "two"], after="swap")
    assert json.loads(h2["HX-Trigger-After-Swap"]) == {"one": True, "two": True}

    # mapping payload
    h3 = hx_trigger_headers({"evt": {"id": 1}}, after="settle")
    assert json.loads(h3["HX-Trigger-After-Settle"]) == {"evt": {"id": 1}}


def test_partial_html_headers_and_body() -> None:
    resp = partial_html("<div>ok</div>", triggers="greeble:done", headers={"X-Test": "1"})
    assert isinstance(resp, HTMLResponse)
    assert resp.status_code == 200
    assert resp.headers["X-Test"] == "1"
    assert json.loads(resp.headers["HX-Trigger"]) == {"greeble:done": True}
    assert resp.body == b"<div>ok</div>"


def write_template(dirpath: Path, name: str, content: str) -> None:
    file = dirpath / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def build_app_with_templates(tmp_path: Path) -> tuple[FastAPI, Jinja2Templates]:
    tpl_dir = tmp_path / "templates"
    write_template(tpl_dir, "layout.html", "FULL {{ msg }}")
    write_template(tpl_dir, "partial.html", "PART {{ msg }}")
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/")
    def root(request: Request) -> Response:
        return template_response(
            templates,
            "layout.html",
            {"msg": "hi"},
            request,
            partial_template="partial.html",
        )

    @app.get("/trigger")
    def with_trigger(request: Request) -> Response:
        return template_response(
            templates,
            "layout.html",
            {"msg": "hi"},
            request,
            partial_template="partial.html",
            triggers={"evt": {"ok": True}},
        )

    return app, templates


def test_template_response_switches_on_hx(tmp_path: Path) -> None:
    app, _ = build_app_with_templates(tmp_path)
    client = TestClient(app)

    # Without HX header -> full layout
    r1 = client.get("/")
    assert r1.status_code == 200
    assert r1.text == "FULL hi"

    # With HX header -> partial
    r2 = client.get("/", headers={HX_REQUEST_HEADER: "true"})
    assert r2.status_code == 200
    assert r2.text == "PART hi"


def test_template_response_attaches_triggers(tmp_path: Path) -> None:
    app, _ = build_app_with_templates(tmp_path)
    client = TestClient(app)

    r = client.get("/trigger", headers={HX_REQUEST_HEADER: "true"})
    assert r.status_code == 200
    assert "HX-Trigger" in r.headers
    assert json.loads(r.headers["HX-Trigger"]) == {"evt": {"ok": True}}
