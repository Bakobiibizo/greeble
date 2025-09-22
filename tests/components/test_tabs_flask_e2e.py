from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_tabs_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "tabs" / "templates"
    assert tpl_dir.exists(), f"missing tabs templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "tabs.html")

    partial_html = (tpl_dir / "tabs.partial.html").read_text(encoding="utf-8")

    @app.get("/tabs/{tab_key}", response_class=HTMLResponse)
    def load_tab(tab_key: str) -> HTMLResponse:
        html = partial_html.replace('data-tab="overview"', f'data-tab="{tab_key}"')
        return HTMLResponse(html)

    return app


def test_tabs_home_renders() -> None:
    app = build_tabs_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-tabs"' in r.text
    assert 'hx-get="/tabs/overview"' in r.text


def test_tab_partial_endpoint() -> None:
    app = build_tabs_app()
    client = TestClient(app)

    r = client.get("/tabs/overview")
    assert r.status_code == 200
    assert "Mission control" in r.text
