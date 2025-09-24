from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
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


@pytest.fixture
def app() -> FastAPI:
    return build_inputs_app()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def _post_validate(client: TestClient, value: str) -> Any:
    return client.post("/input/validate", data={"value": value})


def test_inputs_render(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert 'class="greeble-input"' in r.text


def test_inputs_validate_endpoint(client: TestClient) -> None:
    r_bad = _post_validate(client, "nope")
    assert r_bad.status_code == 400
    assert 'data-greeble-error="true"' in r_bad.text

    r_ok = _post_validate(client, "user@example.com")
    assert r_ok.status_code == 200
    assert "greeble-input-ok" in r_ok.text


def test_inputs_validate_empty_and_whitespace(client: TestClient) -> None:
    r_empty = _post_validate(client, "")
    assert r_empty.status_code == 400
    r_ws = _post_validate(client, "   ")
    assert r_ws.status_code == 400


def test_inputs_validate_long_strings(client: TestClient) -> None:
    long_invalid = "a" * 512
    r_long_invalid = _post_validate(client, long_invalid)
    assert r_long_invalid.status_code == 400

    long_valid = ("a" * 256) + "@example.com"
    r_long_valid = _post_validate(client, long_valid)
    assert r_long_valid.status_code == 200
    assert "greeble-input-ok" in r_long_valid.text


def test_inputs_validate_multiple_at_symbols_current_behavior(client: TestClient) -> None:
    # Current simplistic validator only checks for presence of '@', so this passes.
    r = _post_validate(client, "user@@example.com")
    assert r.status_code == 200
    assert "greeble-input-ok" in r.text
