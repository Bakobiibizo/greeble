from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from starlette.testclient import TestClient

from greeble.adapters.fastapi import HX_REQUEST_HEADER, template_response


def build_modal_app() -> FastAPI:
    root = Path(__file__).resolve().parents[2]
    modal_tpl_dir = root / "packages" / "greeble_components" / "components" / "modal" / "templates"
    assert modal_tpl_dir.exists(), f"missing modal templates at {modal_tpl_dir}"
    templates = Jinja2Templates(directory=str(modal_tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        # Use the trigger markup as the home page content
        return templates.TemplateResponse(request, "modal.html")

    @app.get("/modal/example", response_class=HTMLResponse)
    def modal_example(request: Request) -> Response:
        # Render the modal partial in response to an HTMX request
        return template_response(
            templates,
            template_name="modal.partial.html",
            context={},
            request=request,
            partial=True,
            partial_template="modal.partial.html",
        )

    @app.get("/modal/close", response_class=HTMLResponse)
    def modal_close() -> HTMLResponse:
        return HTMLResponse("")

    @app.post("/modal/submit", response_class=HTMLResponse)
    def modal_submit(email: str = Form(...)) -> HTMLResponse:
        # Return an out-of-band toast fragment announcing success
        html = f"""
        <div id=\"greeble-toasts\" hx-swap-oob=\"true\">
          <div class=\"greeble-toast greeble-toast--success\">Saved {email}</div>
        </div>
        """
        return HTMLResponse(html)

    return app


def _modal_client() -> TestClient:
    return TestClient(build_modal_app())


def test_home_and_open_modal_flow() -> None:
    client = _modal_client()

    # Home page contains trigger markup and modal root
    r = client.get("/")
    assert r.status_code == 200
    assert 'hx-get="/modal/example"' in r.text
    assert 'id="modal-root"' in r.text

    # Request the modal partial via HTMX
    r2 = client.get("/modal/example", headers={HX_REQUEST_HEADER: "true"})
    assert r2.status_code == 200
    assert 'id="greeble-modal"' in r2.text
    assert 'role="dialog"' in r2.text

    # Close returns empty fragment
    r3 = client.get("/modal/close")
    assert r3.status_code == 200
    assert r3.text == ""


def test_modal_submit_returns_oob_toast() -> None:
    client = _modal_client()

    r = client.post("/modal/submit", data={"email": "user@example.com"})
    assert r.status_code == 200
    # Verify an out-of-band toast is present in the response body
    assert 'id="greeble-toasts"' in r.text
    assert "Saved user@example.com" in r.text


def test_modal_submit_missing_email() -> None:
    client = _modal_client()

    r = client.post("/modal/submit", data={})
    assert r.status_code == 422
