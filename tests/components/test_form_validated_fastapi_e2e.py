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

    email_partial = (tpl_dir / "form.partial.html").read_text(encoding="utf-8")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        return templates.TemplateResponse(request, "form.html")

    @app.post("/form/validate", response_class=HTMLResponse)
    def validate(request: Request, email: str = Form("")) -> Response:
        if not email or "@" not in email:
            return HTMLResponse(email_partial, status_code=400)
        valid_html = """
<div id="form-email-group" class="greeble-field" hx-swap-oob="true"
     hx-post="/form/validate"
     hx-trigger="change from:#form-email, keyup delay:400ms from:#form-email, blur from:#form-email"
     hx-target="#form-email-group"
     hx-swap="outerHTML"
     hx-include="#form-email">
  <label class="greeble-field__label" for="form-email">Work email</label>
  <input class="greeble-input" id="form-email" name="email" type="email"
         autocomplete="email" aria-describedby="form-email-hint" required />
  <p class="greeble-field__hint" id="form-email-hint">
    Use your company domain for faster approval.
  </p>
</div>
        """
        return HTMLResponse(valid_html)

    @app.post("/form/submit", response_class=HTMLResponse)
    def submit(email: str = Form("")) -> HTMLResponse:
        if not email or "@" not in email:
            return HTMLResponse(email_partial, status_code=400)
        toast = (
            '<div id="greeble-toasts" hx-swap-oob="true">'
            f'<div class="greeble-toast greeble-toast--success" role="status">'
            f"Request received for {email}."
            "</div>"
            "</div>"
        )
        status = '<p class="greeble-validated-form__support">We\'ll reach out with next steps.</p>'
        return HTMLResponse(toast + status)

    return app


def _form_client() -> TestClient:
    return TestClient(build_form_app())


def test_form_renders() -> None:
    client = _form_client()

    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-validated-form"' in r.text
    assert 'id="form-email-group"' in r.text


def test_form_validate_endpoint() -> None:
    client = _form_client()

    r_bad = client.post("/form/validate", data={"email": "nope"})
    assert r_bad.status_code == 400
    assert "greeble-field--invalid" in r_bad.text

    r_missing = client.post("/form/validate", data={})
    assert r_missing.status_code == 400
    assert "greeble-field--invalid" in r_missing.text

    r_ok = client.post("/form/validate", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    assert "form-email" in r_ok.text


def test_form_submit_flow() -> None:
    client = _form_client()

    r_bad = client.post("/form/submit", data={"email": "bad"})
    assert r_bad.status_code == 400
    assert "greeble-field--invalid" in r_bad.text

    r_missing = client.post("/form/submit", data={})
    assert r_missing.status_code == 400
    assert "greeble-field--invalid" in r_missing.text

    r_ok = client.post("/form/submit", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    assert 'id="greeble-toasts"' in r_ok.text
    assert "Request received" in r_ok.text
