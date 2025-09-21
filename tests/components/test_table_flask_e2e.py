from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template, request
from flask import Response as FlaskResponse

from greeble.adapters.flask import partial_html


def build_table_app() -> Flask:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "table" / "templates"
    assert tpl_dir.exists(), f"missing table templates at {tpl_dir}"

    app = Flask(__name__, template_folder=str(tpl_dir))

    @app.get("/")
    def home() -> str:
        # Serve base table page with tbody target and pagination container
        return render_template("table.html")

    @app.get("/table")
    def table() -> FlaskResponse:
        # Simulate server pagination/sort by echoing params in the row for test visibility
        page = request.args.get("page", "1")
        sort = request.args.get("sort", "")
        html = f"<tr><td>Row page={page} sort={sort}</td></tr>"
        return partial_html(html)

    return app


def test_table_home_renders() -> None:
    app = build_table_app()
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert '<tbody id="table-body">' in text
    assert '<nav class="greeble-pagination">' in text


def test_table_endpoint_returns_partial_and_respects_query() -> None:
    app = build_table_app()
    client = app.test_client()

    r = client.get("/table", query_string={"page": 2, "sort": "name:asc"})
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert "<tr>" in text and "</tr>" in text
    assert "page=2" in text
    assert "sort=name:asc" in text
