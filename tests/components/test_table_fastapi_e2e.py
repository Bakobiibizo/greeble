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
        return templates.TemplateResponse("table.html", {"request": request})

    @app.get("/table", response_class=HTMLResponse)
    def table(request: Request) -> HTMLResponse:
        # Simulate server pagination/sort by echoing params in the row for test visibility
        q = request.query_params
        page = q.get("page", "1")
        sort = q.get("sort", "")
        html = f"<tr><td>Row page={page} sort={sort}</td></tr>"
        return HTMLResponse(html)

    return app


def test_table_home_renders() -> None:
    app = build_table_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert '<tbody id="table-body">' in r.text
    assert '<nav class="greeble-pagination">' in r.text


def test_table_endpoint_returns_partial_and_respects_query() -> None:
    app = build_table_app()
    client = TestClient(app)

    r = client.get("/table", params={"page": 2, "sort": "name:asc"})
    assert r.status_code == 200
    assert "<tr>" in r.text and "</tr>" in r.text
    assert "page=2" in r.text
    assert "sort=name:asc" in r.text
