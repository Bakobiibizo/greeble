from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template
from flask import Response as FlaskResponse


def build_toast_app() -> Flask:
    # We can serve the toast root template as the home page content.
    root = Path(__file__).resolve().parents[2]
    toast_tpl_dir = root / "packages" / "greeble_components" / "components" / "toast" / "templates"
    assert toast_tpl_dir.exists(), f"missing toast templates at {toast_tpl_dir}"

    app = Flask(__name__, template_folder=str(toast_tpl_dir))

    @app.get("/")
    def home() -> str:
        # Serve the toast root container
        return render_template("toast.root.html")

    @app.post("/notify")
    def notify() -> FlaskResponse:
        # Return an out-of-band update that appends a toast item
        html = (
            '<div id="greeble-toasts" hx-swap-oob="true">'
            '<div class="greeble-toast greeble-toast--info" role="status">Hello!</div>'
            "</div>"
        )
        from greeble.adapters.flask import partial_html

        return partial_html(html)

    return app


def test_toast_root_is_served() -> None:
    app = build_toast_app()
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'id="greeble-toasts"' in text


def test_notify_returns_oob_toast() -> None:
    app = build_toast_app()
    client = app.test_client()

    r = client.post("/notify")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'hx-swap-oob="true"' in text
    assert 'class="greeble-toast' in text
    assert 'role="status"' in text
