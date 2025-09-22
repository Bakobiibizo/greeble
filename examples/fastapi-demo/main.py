from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path
from string import Template

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from greeble.adapters.fastapi import template_response

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8050))

# Resolve repo root to point Jinja2 at component template folders
ROOT = Path(__file__).resolve().parents[2]
CPTS = ROOT / "packages" / "greeble_components" / "components"

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

# Serve core CSS for basic styling
app.mount(
    "/static/greeble",
    StaticFiles(directory=str(ROOT / "packages" / "greeble_core" / "assets" / "css")),
    name="greeble-static",
)


def render_page(title: str, body_html: str) -> HTMLResponse:
    """Return a minimal HTML page that includes HTMX and core styles."""
    html_tpl = Template(
        """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>$title</title>
        <link rel="stylesheet" href="/static/greeble/greeble-core.css" />
        <style>
          body {
            font-family: system-ui, -apple-system, Segoe UI,
              Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif;
            padding: 2rem;
          }
          main { display: grid; gap: 1rem; }
          table, th, td { border: 1px solid #2a2a32; border-collapse: collapse; }
          th, td { padding: .5rem .75rem; }
          .stack { display: grid; gap: .75rem; }
          .cluster { display: flex; gap: .5rem; flex-wrap: wrap; align-items: center; }
          .demo-card { padding: 1rem; border: 1px solid #2a2a32; border-radius: 10px; }
        </style>
        <script src="https://unpkg.com/htmx.org@1.9.12"></script>
        <script src="https://unpkg.com/htmx.org/dist/ext/sse.js"></script>
      </head>
      <body>
        <header class="cluster">
          <a href="/">Home</a>
          <strong>Greeble FastAPI Demo</strong>
        </header>
        <main class="stack">
          <div class="demo-card">$body_html</div>
        </main>
      </body>
    </html>
    """
    )
    return HTMLResponse(html_tpl.substitute(title=title, body_html=body_html))


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    items = [
        ("/demo/button", "Buttons (page)"),
        ("/demo/input", "Inputs (page)"),
        ("/demo/dropdown", "Dropdown (page)"),
        ("/demo/tabs", "Tabs (page) + GET /tabs/{tabKey}"),
        ("/demo/table", "Table (page) + GET /table?page=&sort="),
        ("/demo/modal", "Modal (page) + GET /modal/example, /modal/close, POST /modal/submit"),
        ("/demo/toast", "Toasts (page) + POST /notify (OOB)"),
        ("/demo/drawer", "Drawer (page) + GET /drawer/open, /drawer/close"),
        ("/demo/palette", "Palette (page) + POST /palette/search"),
        ("/demo/stepper", "Stepper (page) + GET /stepper/{stepKey}"),
        ("/demo/infinite-list", "Infinite List (page) + GET /list"),
        ("/demo/sse", "SSE demo (page) + GET /stream -> OOB fragments"),
    ]
    lis = "\n".join([f'<li><a href="{href}">{label}</a></li>' for href, label in items])
    return render_page(
        "Demo Index",
        f"""
        <h1>Greeble FastAPI Demo</h1>
        <p>Pages render trigger markup. Use the UI to call HTMX partial endpoints.</p>
        <ul>
        {lis}
        </ul>
        """,
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
    return HTMLResponse(f"<tr><td>Row page={page} sort={sort}</td></tr>")


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
    html = '<ul role="listbox"><li role="option">Result</li></ul>'
    return HTMLResponse(html)


# --- Stepper --------------------------------------------------------------------


@app.get("/demo/stepper", response_class=HTMLResponse)
def stepper_page(request: Request) -> Response:
    body = (CPTS / "stepper" / "templates" / "stepper.html").read_text(encoding="utf-8")
    return render_page("Stepper", body)


@app.get("/stepper/{stepKey}", response_class=HTMLResponse)
def stepper_partial(stepKey: str) -> HTMLResponse:  # noqa: ARG001
    return HTMLResponse("<section>Step content</section>")


# --- Infinite List --------------------------------------------------------------


@app.get("/demo/infinite-list", response_class=HTMLResponse)
def infinite_list_page(request: Request) -> Response:
    body = (CPTS / "infinite-list" / "templates" / "infinite-list.html").read_text(encoding="utf-8")
    return render_page("Infinite List", body)


@app.get("/list", response_class=HTMLResponse)
def infinite_list_items() -> HTMLResponse:
    return HTMLResponse("<li>New Item</li>")


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
