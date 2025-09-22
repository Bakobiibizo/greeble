from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_palette_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "palette" / "templates"
    assert tpl_dir.exists(), f"missing palette templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "palette.html")

    @app.post("/palette/search", response_class=HTMLResponse)
    def search(q: str = Form("")) -> HTMLResponse:
        # Return results partial (ignore query content for placeholder)
        html = '<ul role="listbox"><li role="option">Result</li></ul>'
        return HTMLResponse(html)

    return app


def test_palette_home_renders() -> None:
    app = build_palette_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'hx-post="/palette/search"' in r.text
    assert 'id="palette-results"' in r.text


def test_palette_search_returns_partial() -> None:
    app = build_palette_app()
    client = TestClient(app)

    r = client.post("/palette/search", data={"q": "abc"})
    assert r.status_code == 200
    assert 'role="listbox"' in r.text
    assert 'role="option"' in r.text
