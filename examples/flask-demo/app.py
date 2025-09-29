from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from flask import Flask, render_template, request
from werkzeug.middleware.shared_data import SharedDataMiddleware

from greeble.adapters import flask as g_flask

app = Flask(__name__)

# Mount canonical core assets and repo public images under /static/
ROOT = Path(__file__).resolve().parents[2]
CORE_ASSETS = ROOT / "packages" / "greeble_core" / "assets" / "css"
HYPERSCRIPT_ASSETS = ROOT / "packages" / "greeble_hyperscript" / "assets"
app.wsgi_app = SharedDataMiddleware(  # type: ignore[assignment]
    app.wsgi_app,
    {
        "/static/greeble": str(CORE_ASSETS),
        "/static/greeble/hyperscript": str(HYPERSCRIPT_ASSETS),
        "/static/images": str(ROOT / "public" / "images"),
    },
)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/panel")
def panel():
    context: dict[str, Any] = {"message": "Panel loaded via HTMX"}
    return g_flask.template_response(
        template_name="panel.html",
        partial_template="panel.partial.html",
        context=context,
        request=request,
        triggers={"greeble:toast": {"level": "info", "message": "Loaded panel"}},
    )


if __name__ == "__main__":
    debug = bool(os.getenv("FLASK_DEBUG"))
    app.run(debug=debug)
