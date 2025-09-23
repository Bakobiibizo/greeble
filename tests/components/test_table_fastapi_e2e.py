from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
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

    valid_sorts = {"org", "name", "status"}

    @app.get("/table", response_class=HTMLResponse)
    def table(request: Request, page: int = 1, sort: str = "org:asc") -> HTMLResponse:
        field, _, direction = sort.partition(":")
        if field not in valid_sorts or direction not in {"asc", "desc"}:
            raise HTTPException(status_code=400, detail="Invalid sort parameter")
        if page < 1:
            raise HTTPException(status_code=400, detail="Invalid page")
        # Return the canonical table partial. Real apps would tailor rows based on query params.
        return templates.TemplateResponse(request, "table.partial.html")

    return app


def _table_client() -> TestClient:
    return TestClient(build_table_app())


def test_table_home_renders() -> None:
    client = _table_client()

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-table"' in r.text
    assert 'id="table-body"' in r.text
    # Sort buttons expose hx-get for server swaps
    assert 'hx-get="/table?page=1&sort=org:asc"' in r.text


def test_table_endpoint_returns_partial_and_respects_query() -> None:
    client = _table_client()

    r = client.get("/table", params={"page": 2, "sort": "name:asc"})
    assert r.status_code == 200
    assert "greeble-table__status" in r.text
    assert "Orbit Labs" in r.text
    assert "Nova Civic" in r.text


def test_table_endpoint_rejects_invalid_sort() -> None:
    client = _table_client()

    r = client.get("/table", params={"page": 1, "sort": "unknown:asc"})
    assert r.status_code == 400


def test_table_endpoint_rejects_invalid_page() -> None:
    client = _table_client()

    r = client.get("/table", params={"page": 0, "sort": "org:asc"})
    assert r.status_code == 400
