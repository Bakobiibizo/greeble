from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_table_app() -> FastAPI:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "table" / "templates"
    assert tpl_dir.exists(), f"missing table templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        # Serve base table page with tbody target and pagination container
        return templates.TemplateResponse(request, "table.html")

    @app.get("/table", response_class=HTMLResponse)
    def table(request: Request) -> HTMLResponse:
        # Return the canonical table partial. Real apps would tailor rows based on query params.
        return templates.TemplateResponse(request, "table.partial.html")

    return app


def test_table_home_renders() -> None:
    app = build_table_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-table"' in r.text
    assert 'id="table-body"' in r.text
    # Sort buttons expose hx-get for server swaps
    assert 'hx-get="/table?page=1&sort=org:asc"' in r.text


def test_table_endpoint_returns_partial_and_respects_query() -> None:
    app = build_table_app()
    client = TestClient(app)

    r = client.get("/table", params={"page": 2, "sort": "name:asc"})
    assert r.status_code == 200
    assert "greeble-table__status" in r.text
    assert "Orbit Labs" in r.text
    assert "Nova Civic" in r.text
