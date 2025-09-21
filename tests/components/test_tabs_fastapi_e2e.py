from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.testclient import TestClient


def build_tabs_app() -> FastAPI:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "tabs" / "templates"
    assert tpl_dir.exists(), f"missing tabs templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        return templates.TemplateResponse("tabs.html", {"request": request})

    @app.get("/tabs/{tabKey}", response_class=HTMLResponse)
    def tab_partial(tabKey: str) -> HTMLResponse:
        # Return a dynamic fragment for the given tab
        return HTMLResponse(f"<section>Content for {tabKey}</section>")

    return app


def test_tabs_home_renders() -> None:
    app = build_tabs_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'role="tablist"' in r.text
    assert 'hx-get="/tabs/one"' in r.text
    assert 'hx-get="/tabs/two"' in r.text
    assert 'id="tab-panel"' in r.text


def test_tabs_endpoint_returns_partial() -> None:
    app = build_tabs_app()
    client = TestClient(app)

    r = client.get("/tabs/alpha")
    assert r.status_code == 200
    assert "Content for alpha" in r.text
