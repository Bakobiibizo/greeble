from __future__ import annotations

from pathlib import Path

from flask import Flask, request
from flask import Response as FlaskResponse

from greeble.adapters.flask import HX_REQUEST_HEADER, template_response


def build_modal_app() -> Flask:
    root = Path(__file__).resolve().parents[2]
    modal_tpl_dir = root / "packages" / "greeble_components" / "components" / "modal" / "templates"
    assert modal_tpl_dir.exists(), f"missing modal templates at {modal_tpl_dir}"

    app = Flask(__name__, template_folder=str(modal_tpl_dir))

    @app.get("/")
    def home() -> FlaskResponse:
        # Use the trigger markup as the home page content
        return template_response("modal.html", {}, request, partial=False)

    @app.get("/modal/example")
    def modal_example() -> FlaskResponse:
        # Render the modal partial in response to an HTMX request
        return template_response(
            template_name="modal.partial.html",
            context={},
            req=request,
            partial=True,
            partial_template="modal.partial.html",
        )

    @app.get("/modal/close")
    def modal_close() -> FlaskResponse:
        from greeble.adapters.flask import partial_html

        return partial_html("")

    @app.post("/modal/submit")
    def modal_submit() -> FlaskResponse:
        email = request.form.get("email", "")
        html = f"""
        <div id=\"greeble-toasts\" hx-swap-oob=\"true\">
          <div class=\"greeble-toast greeble-toast--success\">Saved {email}</div>
        </div>
        """
        from greeble.adapters.flask import partial_html

        return partial_html(html)

    return app


def test_home_and_open_modal_flow() -> None:
    app = build_modal_app()
    client = app.test_client()

    # Home page contains trigger markup and modal root
    r = client.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'hx-get="/modal/example"' in text
    assert 'id="modal-root"' in text

    # Request the modal partial via HTMX
    r2 = client.get("/modal/example", headers={HX_REQUEST_HEADER: "true"})
    assert r2.status_code == 200
    body2 = r2.get_data(as_text=True)
    assert 'id="greeble-modal"' in body2
    assert 'role="dialog"' in body2

    # Close returns empty fragment
    r3 = client.get("/modal/close")
    assert r3.status_code == 200
    assert r3.get_data(as_text=True) == ""


def test_modal_submit_returns_oob_toast() -> None:
    app = build_modal_app()
    client = app.test_client()

    r = client.post("/modal/submit", data={"email": "user@example.com"})
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    # Verify an out-of-band toast is present in the response body
    assert 'id="greeble-toasts"' in body
    assert "Saved user@example.com" in body
