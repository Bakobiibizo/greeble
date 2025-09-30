from __future__ import annotations

import asyncio
import os
import textwrap
from collections.abc import AsyncIterator
from pathlib import Path
from string import Template

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from examples.shared.assets import apply_fastapi_assets, head_markup
from greeble.adapters.fastapi import template_response

from .data import INFINITE_ITEMS, STEP_CONTENT
from .renderers import render_palette_results, render_table

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8050))

# Resolve repo root to point Jinja2 at component template folders
ROOT = Path(__file__).resolve().parents[2]
CPTS = ROOT / "packages" / "greeble_components" / "components"


_infinite_index = 0

# One Jinja2Templates per component folder (simplest; avoids multi-dir engine wiring)
T_BUTTON = Jinja2Templates(directory=str(CPTS / "button" / "templates"))
T_INPUT = Jinja2Templates(directory=str(CPTS / "input" / "templates"))
T_DROPDOWN = Jinja2Templates(directory=str(CPTS / "dropdown" / "templates"))
T_TABS = Jinja2Templates(directory=str(CPTS / "tabs" / "templates"))
T_TABLE = Jinja2Templates(directory=str(CPTS / "table" / "templates"))
T_MODAL = Jinja2Templates(directory=str(CPTS / "modal" / "templates"))
T_TOAST = Jinja2Templates(directory=str(CPTS / "toast" / "templates"))
T_DRAWER = Jinja2Templates(directory=str(CPTS / "drawer" / "templates"))
T_PALETTE = Jinja2Templates(directory=str(CPTS / "palette" / "templates"))
T_STEPPER = Jinja2Templates(directory=str(CPTS / "stepper" / "templates"))
T_INF_LIST = Jinja2Templates(directory=str(CPTS / "infinite-list" / "templates"))

app = FastAPI(title="Greeble FastAPI Demo")
apply_fastapi_assets(app)


def render_page(title: str, body_html: str) -> HTMLResponse:
    """Render canonical layout with shared assets and toast region."""

    html_tpl = Template(
        textwrap.dedent(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>$title</title>
                $assets
              </head>
              <body>
                <header class="site-header">
                  <div class="cluster">
                    <strong>Greeble FastAPI Demo</strong>
                    <nav class="cluster" aria-label="Demo navigation">
                      <a href="/">Home</a>
                    </nav>
                  </div>
                  <div class="cluster">
                    <a class="greeble-button greeble-button--ghost" href="https://github.com/bakobiibizo/greeble">Source</a>
                  </div>
                </header>
                <div id="greeble-toasts" class="greeble-toast-region" aria-live="polite" aria-label="Notifications"></div>
                <main class="site-main">
                  <div class="card stack">$body_html</div>
                </main>
              </body>
            </html>
            """
        )
    )
    return HTMLResponse(html_tpl.substitute(title=title, body_html=body_html, assets=head_markup()))


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    items = [
        ("/demo/button", "Buttons (page)"),
        ("/demo/input", "Inputs (page)"),
        ("/demo/dropdown", "Dropdown (page)"),
        ("/demo/tabs", "Tabs (page) + GET /tabs/{tabKey}"),
        ("/demo/table", "Table (page) + GET /table?page=&sort="),
        ("/demo/modal", "Modal (page) + GET /modal/example, /modal/close, POST /modal/submit"),
        ("/demo/toast", "Toasts (page) + POST /notify"),
        ("/demo/drawer", "Drawer (page) + GET /drawer/open, /drawer/close"),
        ("/demo/palette", "Palette (page) + POST /palette/search"),
        ("/demo/stepper", "Stepper (page) + GET /stepper/{stepKey}"),
        ("/demo/infinite-list", "Infinite List (page) + GET /list"),
        ("/demo/sse", "SSE demo (page) + GET /stream"),
    ]
    lis = "\n".join([f'<li><a href="{href}">{label}</a></li>' for href, label in items])
    return render_page(
        "Demo Index",
        textwrap.dedent(
            f"""
            <div class="stack">
              <h1 class="text-gradient">Greeble FastAPI Demo</h1>
              <p>Pages render trigger markup. Use the UI to call HTMX partial endpoints.</p>
              <ul class="stack" style="list-style:none; padding:0; margin:0; text-align:left;">
              {lis}
              </ul>
            </div>
            """
        ).strip(),
    )


# --- Button ---------------------------------------------------------------------


@app.get("/demo/button", response_class=HTMLResponse)
def button_page(request: Request) -> Response:
    body = (CPTS / "button" / "templates" / "button.html").read_text(encoding="utf-8")
    return render_page("Buttons", body)


# --- Inputs ---------------------------------------------------------------------


@app.get("/demo/input", response_class=HTMLResponse)
def input_page(request: Request) -> Response:
    body = (CPTS / "input" / "templates" / "input.html").read_text(encoding="utf-8")
    return render_page("Inputs", body)


# --- Dropdown -------------------------------------------------------------------


@app.get("/demo/dropdown", response_class=HTMLResponse)
def dropdown_page(request: Request) -> Response:
    body = (CPTS / "dropdown" / "templates" / "dropdown.html").read_text(encoding="utf-8")
    return render_page("Dropdown", body)


# --- Tabs -----------------------------------------------------------------------


@app.get("/demo/tabs", response_class=HTMLResponse)
def tabs_page(request: Request) -> Response:
    body = (CPTS / "tabs" / "templates" / "tabs.html").read_text(encoding="utf-8")
    return render_page("Tabs", body)


@app.get("/tabs/{tabKey}", response_class=HTMLResponse)
def tabs_partial(tabKey: str) -> HTMLResponse:  # noqa: N803 - param name style
    return HTMLResponse(f"<section>Content for {tabKey}</section>")


# --- Table ----------------------------------------------------------------------


@app.get("/demo/table", response_class=HTMLResponse)
def table_page(request: Request) -> Response:
    body = (CPTS / "table" / "templates" / "table.html").read_text(encoding="utf-8")
    return render_page("Table", body)


@app.get("/table", response_class=HTMLResponse)
def table_rows(request: Request) -> HTMLResponse:
    q = request.query_params
    page = q.get("page", "1")
    sort = q.get("sort", "")
    query = q.get("query", "")
    return HTMLResponse(render_table(page=page, sort=sort, query=query))


# --- Modal ----------------------------------------------------------------------


@app.get("/demo/modal", response_class=HTMLResponse)
def modal_page(request: Request) -> Response:
    body = (CPTS / "modal" / "templates" / "modal.html").read_text(encoding="utf-8")
    return render_page("Modal", body)


@app.get("/modal/example", response_class=HTMLResponse)
def modal_example(request: Request) -> Response:
    return template_response(
        T_MODAL,
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
def modal_submit(email: str = Form("")) -> HTMLResponse:
    html = (
        '<div id="greeble-toasts" hx-swap-oob="true">'
        f'<div class="greeble-toast greeble-toast--success">Saved {email}</div>'
        "</div>"
    )
    return HTMLResponse(html)


# --- Toasts ---------------------------------------------------------------------


@app.get("/demo/toast", response_class=HTMLResponse)
def toast_page(request: Request) -> Response:
    body = (CPTS / "toast" / "templates" / "toast.root.html").read_text(encoding="utf-8")
    return render_page("Toasts", body)


@app.post("/notify", response_class=HTMLResponse)
def notify() -> HTMLResponse:
    html = (
        '<div id="greeble-toasts" hx-swap-oob="true">'
        '<div class="greeble-toast greeble-toast--info" role="status">Hello!</div>'
        "</div>"
    )
    return HTMLResponse(html)


# --- Drawer ---------------------------------------------------------------------


@app.get("/demo/drawer", response_class=HTMLResponse)
def drawer_page(request: Request) -> Response:
    body = (CPTS / "drawer" / "templates" / "drawer.html").read_text(encoding="utf-8")
    return render_page("Drawer", body)


@app.get("/drawer/open", response_class=HTMLResponse)
def drawer_open(request: Request) -> Response:
    return template_response(
        T_DRAWER,
        template_name="drawer.partial.html",
        context={},
        request=request,
        partial=True,
        partial_template="drawer.partial.html",
    )


@app.get("/drawer/close", response_class=HTMLResponse)
def drawer_close() -> HTMLResponse:
    return HTMLResponse("")


# --- Command Palette ------------------------------------------------------------


@app.get("/demo/palette", response_class=HTMLResponse)
def palette_page(request: Request) -> Response:
    body = (CPTS / "palette" / "templates" / "palette.html").read_text(encoding="utf-8")
    return render_page("Palette", body)


@app.post("/palette/search", response_class=HTMLResponse)
def palette_search(q: str = Form("")) -> HTMLResponse:  # noqa: ARG001
    html = render_palette_results(query=q)
    return HTMLResponse(html)


# --- Stepper --------------------------------------------------------------------


@app.get("/demo/stepper", response_class=HTMLResponse)
def stepper_page(request: Request) -> Response:
    body = (CPTS / "stepper" / "templates" / "stepper.html").read_text(encoding="utf-8")
    return render_page("Stepper", body)


@app.get("/stepper/{stepKey}", response_class=HTMLResponse)
def stepper_partial(stepKey: str) -> HTMLResponse:
    content = STEP_CONTENT.get(stepKey)
    if content is None:
        return HTMLResponse("<div class='greeble-card'>Unknown step.</div>", status_code=404)

    items = "".join(f"<li>{item}</li>" for item in content.get("tasks", []))
    body = textwrap.dedent(
        f"""
        <section class="stack" hx-target="#stepper-panel" hx-swap="innerHTML">
          <h3 class="greeble-heading-3">{content["title"]}</h3>
          <p>{content["description"]}</p>
          <ul class="stack">{items}</ul>
        </section>
        """
    ).strip()
    return HTMLResponse(body)


# --- Infinite List --------------------------------------------------------------


@app.get("/demo/infinite-list", response_class=HTMLResponse)
def infinite_list_page(request: Request) -> Response:
    body = (CPTS / "infinite-list" / "templates" / "infinite-list.html").read_text(encoding="utf-8")
    return render_page("Infinite List", body)


@app.get("/list", response_class=HTMLResponse)
def infinite_list_items() -> HTMLResponse:
    global _infinite_index
    item = INFINITE_ITEMS[_infinite_index % len(INFINITE_ITEMS)]
    _infinite_index += 1
    return HTMLResponse(f"<li>{item}</li>")


# --- SSE (Server-Sent Events) Demo --------------------------------------------


@app.get("/demo/sse", response_class=HTMLResponse)
def sse_page() -> HTMLResponse:
    body = (
        "<h2>SSE Demo</h2>"
        '<div id="live-clock">(waiting for server time...)</div>'
        '<div hx-ext="sse" sse-connect="/stream" sse-swap="message"></div>'
        "<p>Server pushes out-of-band fragments updating #live-clock every 2s.</p>"
    )
    return render_page("SSE Demo", body)


async def _clock_stream() -> AsyncIterator[str]:
    # Simple demo stream; in real apps publish from a queue or pub/sub
    while True:
        now = asyncio.get_running_loop().time()
        fragment = f'<div id="live-clock" hx-swap-oob="true">Server time tick: {now:.0f}</div>'
        yield f"data: {fragment}\n\n"
        await asyncio.sleep(2)


@app.get("/stream")
async def sse_stream() -> StreamingResponse:
    return StreamingResponse(_clock_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.fastapi-demo.main:app", host=str(HOST), port=int(PORT), reload=True)
