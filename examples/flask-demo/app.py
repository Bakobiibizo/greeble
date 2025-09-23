from __future__ import annotations

from typing import Any

from flask import Flask, render_template, request

from greeble.adapters import flask as g_flask

app = Flask(__name__)


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
    app.run(debug=True)
