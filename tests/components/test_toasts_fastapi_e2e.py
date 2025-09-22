from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.testclient import TestClient


def build_toast_app() -> FastAPI:
    # We can serve the toast root template as the home page content.
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    toast_tpl_dir = root / "packages" / "greeble_components" / "components" / "toast" / "templates"
    assert toast_tpl_dir.exists(), f"missing toast templates at {toast_tpl_dir}"
    templates = Jinja2Templates(directory=str(toast_tpl_dir))

    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> HTMLResponse:
        # Serve the toast root container
        return templates.TemplateResponse(request, "toast.root.html")

    item_html = (toast_tpl_dir / "toast.item.html").read_text(encoding="utf-8")

    @app.post("/notify", response_class=HTMLResponse)
    def notify() -> HTMLResponse:
        # Return an out-of-band update that appends a toast item
        html = f'<div id="greeble-toasts" hx-swap-oob="true">{item_html}</div>'
        return HTMLResponse(html)

    return app


def test_toast_root_is_served() -> None:
    app = build_toast_app()
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    assert 'id="greeble-toasts"' in r.text


def test_notify_returns_oob_toast() -> None:
    app = build_toast_app()
    client = TestClient(app)

    r = client.post("/notify")
    assert r.status_code == 200
    assert 'hx-swap-oob="true"' in r.text
    assert 'class="greeble-toast greeble-toast--success"' in r.text
    assert 'class="greeble-toast__message"' in r.text
    assert 'role="status"' in r.text
