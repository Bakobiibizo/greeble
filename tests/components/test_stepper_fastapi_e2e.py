from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_stepper_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "stepper" / "templates"
    assert tpl_dir.exists(), f"missing stepper templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(request, "stepper.html")

    partial_html = (tpl_dir / "stepper.partial.html").read_text(encoding="utf-8")

    @app.get("/stepper/plan", response_class=HTMLResponse)
    def plan_step() -> HTMLResponse:
        return HTMLResponse(partial_html)

    @app.get("/stepper/enable", response_class=HTMLResponse)
    def enable_step() -> HTMLResponse:
        return HTMLResponse(partial_html.replace('data-step="plan"', 'data-step="enable"'))

    return app


def test_stepper_home_renders() -> None:
    app = build_stepper_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-stepper"' in r.text
    assert 'data-step="plan"' in r.text
    assert 'id="stepper-panel"' in r.text


def test_stepper_partial_endpoint() -> None:
    app = build_stepper_app()
    client = TestClient(app)

    r = client.get("/stepper/plan")
    assert r.status_code == 200
    assert 'class="greeble-stepper__content"' in r.text
    assert "Continue to enablement" in r.text
