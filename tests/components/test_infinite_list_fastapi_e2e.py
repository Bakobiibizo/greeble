from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_infinite_list_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = (
        root / "packages" / "greeble_components" / "components" / "infinite-list" / "templates"
    )
    assert tpl_dir.exists(), f"missing infinite-list templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("infinite-list.html", {"request": request})

    @app.get("/list", response_class=HTMLResponse)
    def list_items() -> HTMLResponse:
        return HTMLResponse("<li>New Item</li>")

    return app


def test_infinite_list_home_renders() -> None:
    app = build_infinite_list_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'id="infinite-list"' in r.text
    assert 'hx-get="/list"' in r.text


def test_infinite_list_endpoint_returns_partial() -> None:
    app = build_infinite_list_app()
    client = TestClient(app)

    r = client.get("/list")
    assert r.status_code == 200
    assert "<li>New Item</li>" in r.text
