from __future__ import annotations

from pathlib import Path

from flask import Flask, render_template
from flask import Response as FlaskResponse

from greeble.adapters.flask import partial_html


def build_tabs_app() -> Flask:
    root = Path(__file__).resolve().parents[2]
    tpl_dir = root / "packages" / "greeble_components" / "components" / "tabs" / "templates"
    assert tpl_dir.exists(), f"missing tabs templates at {tpl_dir}"

    app = Flask(__name__, template_folder=str(tpl_dir))

    @app.get("/")
    def home() -> str:
        return render_template("tabs.html")

    @app.get("/tabs/<tabKey>")
    def tab_partial(tabKey: str) -> FlaskResponse:  # noqa: N803 - match test param style
        return partial_html(f"<section>Content for {tabKey}</section>")

    return app


def test_tabs_home_renders() -> None:
    app = build_tabs_app()
    client = app.test_client()

    r = client.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'role="tablist"' in text
    assert 'hx-get="/tabs/one"' in text
    assert 'hx-get="/tabs/two"' in text
    assert 'id="tab-panel"' in text


def test_tabs_endpoint_returns_partial() -> None:
    app = build_tabs_app()
    client = app.test_client()

    r = client.get("/tabs/alpha")
    assert r.status_code == 200
    assert "Content for alpha" in r.get_data(as_text=True)
