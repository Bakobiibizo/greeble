from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template, request
from flask import Response as FlaskResponse

from greeble.adapters.flask import partial_html


def build_form_app() -> Flask:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = (
        root / "packages" / "greeble_components" / "components" / "form-validated" / "templates"
    )
    assert tpl_dir.exists(), f"missing form-validated templates at {tpl_dir}"

    app = Flask(__name__, template_folder=str(tpl_dir))

    @app.get("/")
    def home() -> str:
        return render_template("form.html")

    @app.post("/form/validate")
    def validate() -> FlaskResponse:
        email = request.form.get("email", "")
        if not email or "@" not in email:
            # Return an invalid group partial
            html = render_template("form.partial.html")
            resp = partial_html(html, status_code=400)
            return resp
        return partial_html('<div class="greeble-valid">OK</div>')

    @app.post("/form/submit")
    def submit() -> FlaskResponse:
        email = request.form.get("email", "")
        if not email or "@" not in email:
            return partial_html(
                '<div class="form-group form-group--invalid">Invalid</div>', status_code=400
            )
        html = f"""
        <div id=\"greeble-toasts\" hx-swap-oob=\"true\">
          <div class=\"greeble-toast greeble-toast--success\">Submitted {email}</div>
        </div>
        """
        return partial_html(html)

    return app


def test_form_renders() -> None:
    app = build_form_app()
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'class="greeble-input"' in text or 'type="email"' in text


def test_form_validate_endpoint() -> None:
    app = build_form_app()
    client = app.test_client()

    r_bad = client.post("/form/validate", data={"email": "nope"})
    assert r_bad.status_code == 400
    body_bad = r_bad.get_data(as_text=True)
    # Our placeholder partial marks invalid via class
    assert "form-group--invalid" in body_bad or "Error" in body_bad

    r_ok = client.post("/form/validate", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    assert "greeble-valid" in r_ok.get_data(as_text=True)


def test_form_submit_flow() -> None:
    app = build_form_app()
    client = app.test_client()

    r_bad = client.post("/form/submit", data={"email": "bad"})
    assert r_bad.status_code == 400
    assert "form-group--invalid" in r_bad.get_data(as_text=True)

    r_ok = client.post("/form/submit", data={"email": "user@example.com"})
    assert r_ok.status_code == 200
    text_ok = r_ok.get_data(as_text=True)
    assert 'id="greeble-toasts"' in text_ok
    assert "Submitted user@example.com" in text_ok
