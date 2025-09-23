from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.testclient import TestClient

from greeble.adapters.fastapi import HX_REQUEST_HEADER, template_response


def build_drawer_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "drawer" / "templates"
    assert tpl_dir.exists(), f"missing drawer templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "drawer.html")

    @app.get("/drawer/open", response_class=HTMLResponse)
    def open_drawer(request: Request) -> Response:
        return template_response(
            templates,
            template_name="drawer.partial.html",
            context={},
            request=request,
            partial=True,
            partial_template="drawer.partial.html",
        )

    @app.get("/drawer/close", response_class=HTMLResponse)
    def close_drawer() -> HTMLResponse:
        return HTMLResponse("")

    return app


def test_drawer_home_renders() -> None:
    app = build_drawer_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-drawer-trigger"' in r.text
    assert 'hx-get="/drawer/open"' in r.text
    assert 'id="drawer-root"' in r.text


def test_drawer_open_and_close() -> None:
    app = build_drawer_app()
    client = TestClient(app)

    r_open = client.get("/drawer/open", headers={HX_REQUEST_HEADER: "true"})
    assert r_open.status_code == 200
    assert 'class="greeble-drawer__panel"' in r_open.text
    assert "Request walkthrough" in r_open.text

    r_close = client.get("/drawer/close")
    assert r_close.status_code == 200
    assert r_close.text == ""
