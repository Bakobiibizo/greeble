from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.testclient import TestClient


def build_form_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = (
        root / "packages" / "greeble_components" / "components" / "form-validated" / "templates"
    )
    assert tpl_dir.exists(), f"missing form-validated templates at {tpl_dir}"
    templates = Jinja2Templates(directory=str(tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        return templates.TemplateResponse(request, "form.html")

    @app.post("/form/validate", response_class=HTMLResponse)
    def validate(request: Request, email: str = Form("")) -> Response:
        if not email or "@" not in email:
            # Return an invalid group partial
            return templates.TemplateResponse(request, "form.partial.html", status_code=400)
        return HTMLResponse('<div class="greeble-valid">OK</div>')

    @app.post("/form/submit", response_class=HTMLResponse)
    def submit(email: str = Form("")) -> HTMLResponse:
        if not email or "@" not in email:
            return HTMLResponse(
                '<div class="form-group form-group--invalid">Invalid</div>',
                status_code=400,
            )
        html = f"""
        <div id=\"greeble-toasts\" hx-swap-oob=\"true\">
          <div class=\"greeble-toast greeble-toast--success\">Submitted {email}</div>
        </div>
        """
        return HTMLResponse(html)

    return app


def test_form_renders() -> None:
    app = build_form_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-input"' in r.text or 'type="email"' in r.text


def test_form_validate_endpoint() -> None:
    app = build_form_app()
    client = TestClient(app)

    r_bad = client.post("/form/validate", data={"email": "nope"})
    assert r_bad.status_code == 400
    # Our placeholder partial marks invalid via class
    assert "form-group--invalid" in r_bad.text or "Error" in r_bad.text

    r_ok = client.post("/form/validate", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    assert "greeble-valid" in r_ok.text


def test_form_submit_flow() -> None:
    app = build_form_app()
    client = TestClient(app)

    r_bad = client.post("/form/submit", data={"email": "bad"})
    assert r_bad.status_code == 400
    assert "form-group--invalid" in r_bad.text

    r_ok = client.post("/form/submit", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    assert 'id="greeble-toasts"' in r_ok.text
    assert "Submitted user@example.com" in r_ok.text
