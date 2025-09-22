from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_input_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "input" / "templates"
    assert tpl_dir.exists(), f"missing input templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("input.html", {"request": request})

    return app


def test_input_home_renders() -> None:
    app = build_input_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-input"' in r.text
    assert 'type="text"' in r.text
