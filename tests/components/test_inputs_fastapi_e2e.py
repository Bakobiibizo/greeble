from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_inputs_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "input" / "templates"
    assert tpl_dir.exists(), f"missing input templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("input.html", {"request": request})

    @app.post("/input/validate", response_class=HTMLResponse)
    def validate(value: str = Form("")) -> HTMLResponse:
        if not value or "@" not in value:
            html = (
                '<div class="greeble-input-error" data-greeble-error="true" role="alert">'
                "Invalid value</div>"
            )
            return HTMLResponse(html, status_code=400)
        return HTMLResponse('<div class="greeble-input-ok">OK</div>')

    return app


def test_inputs_render() -> None:
    app = build_inputs_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-input"' in r.text


def test_inputs_validate_endpoint() -> None:
    app = build_inputs_app()
    client = TestClient(app)

    r_bad = client.post("/input/validate", data={"value": "nope"})
    assert r_bad.status_code == 400
    assert 'data-greeble-error="true"' in r_bad.text

    r_ok = client.post("/input/validate", data={"value": "user@example.com"})
    assert r_ok.status_code == 200
    assert "greeble-input-ok" in r_ok.text
