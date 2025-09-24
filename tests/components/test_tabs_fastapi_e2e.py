from __future__ import annotations

import pytest
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
        # Only allow known tabs to simulate realistic behavior
        allowed = {"overview", "pricing", "integrations"}
        if tabKey not in allowed:
            return HTMLResponse("Not found", status_code=404)
        return HTMLResponse(f"<section>Content for {tabKey}</section>")

    return app


@pytest.fixture
def app() -> FastAPI:
    return build_tabs_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def test_tabs_home_renders(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert 'role="tablist"' in r.text
    assert 'hx-get="/tabs/overview"' in r.text
    assert 'hx-get="/tabs/pricing"' in r.text
    assert 'id="tab-panel"' in r.text


def test_tabs_endpoint_returns_partial(client: TestClient) -> None:
    r = client.get("/tabs/alpha")
    assert r.status_code == 404

    r_ok = client.get("/tabs/overview")
    assert r_ok.status_code == 200
    assert "Content for overview" in r_ok.text


def test_invalid_tab_key_returns_404(client: TestClient) -> None:
    r = client.get("/tabs/invalid")
    assert r.status_code == 404
