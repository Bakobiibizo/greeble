from __future__ import annotations

import os
from typing import Any

from flask import Flask, render_template, request

from examples.shared.assets import apply_flask_assets
from greeble.adapters import flask as g_flask

app = Flask(__name__)

apply_flask_assets(app)


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
