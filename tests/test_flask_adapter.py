from __future__ import annotations

import json
from pathlib import Path

from flask import Flask

from greeble.adapters.flask import (
    HX_REQUEST_HEADER,
    hx_trigger_headers,
    is_hx_request,
    partial_html,
    template_response,
)


def write_template(dirpath: Path, name: str, content: str) -> None:
    file = dirpath / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")


def build_app_with_templates(tmp_path: Path) -> Flask:
    tpl_dir = tmp_path / "templates"
    write_template(tpl_dir, "layout.html", "FULL {{ msg }}")
    write_template(tpl_dir, "partial.html", "PART {{ msg }}")
    app = Flask(__name__, template_folder=str(tpl_dir))
    return app


def test_is_hx_request_true_false(tmp_path: Path) -> None:
    app = build_app_with_templates(tmp_path)
    with app.test_request_context("/", headers={HX_REQUEST_HEADER: "true"}) as ctx:
        assert is_hx_request(ctx.request) is True
    with app.test_request_context("/", headers={HX_REQUEST_HEADER: "TRUE"}) as ctx:
        assert is_hx_request(ctx.request) is True
    with app.test_request_context("/", headers={HX_REQUEST_HEADER: "false"}) as ctx:
        assert is_hx_request(ctx.request) is False
    with app.test_request_context("/") as ctx:
        assert is_hx_request(ctx.request) is False


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


def test_partial_html_headers_and_body(tmp_path: Path) -> None:
    app = build_app_with_templates(tmp_path)
    with app.app_context():
        resp = partial_html("<div>ok</div>", triggers="greeble:done", headers={"X-Test": "1"})
        assert resp.status_code == 200
        assert resp.headers["X-Test"] == "1"
        assert json.loads(resp.headers["HX-Trigger"]) == {"greeble:done": True}
        assert resp.get_data() == b"<div>ok</div>"


def test_template_response_switches_on_hx(tmp_path: Path) -> None:
    app = build_app_with_templates(tmp_path)
    with app.test_request_context("/") as ctx, app.app_context():
        # Without HX header -> full layout
        r1 = template_response(
            "layout.html",
            {"msg": "hi"},
            ctx.request,
            partial_template="partial.html",
        )
        assert r1.status_code == 200
        assert r1.get_data(as_text=True) == "FULL hi"

    with (
        app.test_request_context(
            "/",
            headers={HX_REQUEST_HEADER: "true"},
        ) as ctx,
        app.app_context(),
    ):
        # With HX header -> partial
        r2 = template_response(
            "layout.html",
            {"msg": "hi"},
            ctx.request,
            partial_template="partial.html",
        )
        assert r2.status_code == 200
        assert r2.get_data(as_text=True) == "PART hi"


def test_template_response_attaches_triggers(tmp_path: Path) -> None:
    app = build_app_with_templates(tmp_path)
    with (
        app.test_request_context(
            "/",
            headers={HX_REQUEST_HEADER: "true"},
        ) as ctx,
        app.app_context(),
    ):
        r = template_response(
            "layout.html",
            {"msg": "hi"},
            ctx.request,
            partial_template="partial.html",
            triggers={"evt": {"ok": True}},
        )
        assert r.status_code == 200
        assert "HX-Trigger" in r.headers
        assert json.loads(r.headers["HX-Trigger"]) == {"evt": {"ok": True}}
