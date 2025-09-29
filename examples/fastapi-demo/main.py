from __future__ import annotations

import asyncio
import json
import os
import textwrap
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from string import Template
from typing import Any

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

# Demo data ---------------------------------------------------------------------

ACCOUNTS: list[dict[str, Any]] = [
    {
        "slug": "orbit-labs",
        "org": "Orbit Labs",
        "owner": "ava@orbitlabs.dev",
        "plan": "Scale",
        "seats": (42, 50),
        "status": "active",
        "renewal": "2025-12-01",
        "notes": "Shipping real-time collaboration tools for orbital ops teams.",
    },
    {
        "slug": "nova-civic",
        "org": "Nova Civic",
        "owner": "sam@nova.city",
        "plan": "Starter",
        "seats": (8, 10),
        "status": "pending",
        "renewal": "2025-04-18",
        "notes": "GovTech consultancy piloting workflow automation across districts.",
    },
    {
        "slug": "comet-ops",
        "org": "Comet Ops",
        "owner": "lin@cometops.io",
        "plan": "Enterprise",
        "seats": (110, 120),
        "status": "delinquent",
        "renewal": "2025-01-05",
        "notes": "Growth-stage logistics platform with dedicated ops pod onboarding.",
    },
    {
        "slug": "aurora-supply",
        "org": "Aurora Supply",
        "owner": "nina@aurorasupply.ai",
        "plan": "Scale",
        "seats": (67, 80),
        "status": "active",
        "renewal": "2026-03-09",
        "notes": "Procurement insights for clean-energy manufacturers.",
    },
    {
        "slug": "helix-health",
        "org": "Helix Health",
        "owner": "dev@helix.health",
        "plan": "Enterprise",
        "seats": (215, 250),
        "status": "active",
        "renewal": "2025-06-30",
        "notes": "Healthcare provider operating multi-region telemedicine clinics.",
    },
]

ACCOUNT_STATUS_BADGES = {
    "active": "greeble-table__status--active",
    "pending": "greeble-table__status--pending",
    "delinquent": "greeble-table__status--delinquent",
}

PALETTE_ENTRIES: list[dict[str, str]] = [
    {
        "slug": "orbit-labs",
        "title": "Orbit Labs",
        "subtitle": "Scale plan · Owner: ava@orbitlabs.dev",
        "shortcut": "O",
    },
    {
        "slug": "nova-civic",
        "title": "Nova Civic",
        "subtitle": "Starter plan · Owner: sam@nova.city",
        "shortcut": "N",
    },
    {
        "slug": "comet-ops",
        "title": "Comet Ops",
        "subtitle": "Enterprise plan · Owner: lin@cometops.io",
        "shortcut": "C",
    },
    {
        "slug": "aurora-supply",
        "title": "Aurora Supply",
        "subtitle": "Scale plan · Owner: nina@aurorasupply.ai",
        "shortcut": "A",
    },
    {
        "slug": "helix-health",
        "title": "Helix Health",
        "subtitle": "Enterprise plan · Owner: dev@helix.health",
        "shortcut": "H",
    },
]

STEP_CONTENT = {
    "plan": "Clarify launch goals, success metrics, and a cross-team timeline before kickoff.",
    "enable": "Distribute enablement briefs, share escalation paths, and confirm support coverage.",
    "launch": "Monitor real-time metrics, announce status updates, and schedule the retro.",
}

INFINITE_ITEMS = [
    "Capture metrics from HQ dashboards",
    "Dispatch approvals to launch team",
    "Schedule release readiness standup",
    "Publish changelog post to community",
    "Archive closed incidents in root cause DB",
    "Rotate API keys for service providers",
    "Send retro invite to stakeholder mailing list",
]

_infinite_index = 0


# Helpers -----------------------------------------------------------------------

Account = dict[str, Any]


def _filter_sort_accounts(sort: str, query: str) -> list[Account]:
    items: list[Account] = list(ACCOUNTS)
    if sort:
        field, _, direction = sort.partition(":")
        reverse = direction.strip().lower() == "desc"

        def key_by_seats(item: Account) -> int:
            used, _ = item["seats"]  # type: ignore[index]
            return used

        def key_by_field(item: Account) -> Any:
            return item.get(field, "")

        key_fn: Callable[[Account], Any]
        key_fn = key_by_seats if field == "seats" else key_by_field
        items.sort(key=key_fn, reverse=reverse)

    if query:
        query_norm = query.lower()
        items = [
            acct
            for acct in items
            if query_norm in acct["org"].lower() or query_norm in acct["owner"].lower()
        ]

    return items


def _render_account_row(account: Account) -> str:
    used, cap = account["seats"]  # type: ignore[index]
    badge_class = ACCOUNT_STATUS_BADGES.get(account["status"], "")
    return textwrap.dedent(
        f"""
        <tr>
          <th scope="row">
            <div class="greeble-table__primary">{account["org"]}</div>
            <p class="greeble-table__meta">Owner: {account["owner"]}</p>
          </th>
          <td>{account["plan"]}</td>
          <td>{used} / {cap}</td>
          <td>
            <span class="greeble-table__status {badge_class}">
              <span aria-hidden="true">●</span>
              {account["status"].title()}
            </span>
          </td>
          <td class="greeble-table__actions">
            <button class="greeble-button greeble-button--ghost" type="button" hx-get="/table/{account["slug"]}" hx-target="#table-inspector" hx-swap="innerHTML">View</button>
            <button class="greeble-button greeble-button--ghost" type="button" hx-post="/table/{account["slug"]}/remind" hx-target="closest tr" hx-swap="none">Send reminder</button>
          </td>
        </tr>
        """
    ).strip()


def _render_table(*, page: str = "1", sort: str = "", query: str = "") -> HTMLResponse:
    query_norm = query.strip().lower()
    rows = _filter_sort_accounts(sort, query_norm)

    try:
        page_num = max(int(page), 1)
    except ValueError:
        page_num = 1

    page_size = 3
    start = (page_num - 1) * page_size
    current = rows[start : start + page_size]

    if not current:
        return HTMLResponse("""<tr><td colspan=5>No accounts match this view.</td></tr>""")

    rendered = [_render_account_row(account) for account in current]
    return HTMLResponse("\n".join(rendered))


def _render_palette_results(entries: list[dict[str, str]]) -> str:
    items = []
    for index, entry in enumerate(entries):
        payload = json.dumps({"slug": entry["slug"]})
        selected = "true" if index == 0 else "false"
        shortcut = entry.get("shortcut", "")
        shortcut_markup = (
            f'<span class="greeble-palette__result-kbd">{shortcut}</span>' if shortcut else ""
        )
        items.append(
            textwrap.dedent(
                f"""
                <li role="option" data-customer="{entry["slug"]}" aria-selected="{selected}">
                  <button
                    class="greeble-palette__result"
                    type="button"
                    hx-post="/palette/select"
                    hx-target="#palette-detail"
                    hx-swap="innerHTML"
                    hx-vals='{payload}'
                  >
                    <div class="greeble-palette__result-label">
                      <strong>{entry["title"]}</strong>
                      <span>{entry["subtitle"]}</span>
                    </div>
                    {shortcut_markup}
                  </button>
                </li>
                """
            ).strip()
        )

    return (
        textwrap.dedent(
            """
        <ul class="greeble-palette__list" role="listbox" aria-label="Customer results">
        """
        )
        + "\n".join(items)
        + "\n</ul>"
    )


def _render_palette_detail(slug: str) -> str:
    account = next((acct for acct in ACCOUNTS if acct["slug"] == slug), None)
    if not account:
        return textwrap.dedent(
            """
            <div class="greeble-palette__detail-empty">
              <p>No customer selected.</p>
            </div>
            """
        ).strip()

    used, cap = account["seats"]
    status_badge = ACCOUNT_STATUS_BADGES.get(account["status"], "")
    return textwrap.dedent(
        f"""
        <div class="stack" style="gap: var(--greeble-spacing-3);">
          <h3 class="greeble-heading-3">{account["org"]}</h3>
          <p><strong>Plan:</strong> {account["plan"]}</p>
          <p><strong>Owner:</strong> {account["owner"]}</p>
          <p><strong>Seats:</strong> {used} of {cap}</p>
          <p>
            <span class="greeble-table__status {status_badge}">
              <span aria-hidden="true">●</span>
              {account["status"].title()}
            </span>
          </p>
          <p>{account["notes"]}</p>
        </div>
        """
    ).strip()


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

# Serve shared assets
app.mount(
    "/static/greeble",
    StaticFiles(directory=str(ROOT / "packages" / "greeble_core" / "assets" / "css")),
    name="greeble-static",
)
app.mount(
    "/static/greeble/hyperscript",
    StaticFiles(directory=str(ROOT / "packages" / "greeble_hyperscript" / "assets")),
    name="greeble-hyperscript",
)
app.mount(
    "/static/images",
    StaticFiles(directory=str(ROOT / "public" / "images")),
    name="greeble-images",
)


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
                <link rel="stylesheet" href="/static/greeble/greeble-core.css" />
                <link rel="stylesheet" href="/static/greeble/greeble-landing.css" />
                <link rel="icon" href="/static/images/greeble-icon-black.svg" type="image/svg+xml" media="(prefers-color-scheme: light)" />
                <link rel="icon" href="/static/images/greeble-icon-alpha-white.png" sizes="any" media="(prefers-color-scheme: dark)" />
                <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>
                <script src="https://unpkg.com/htmx.org/dist/ext/sse.js" defer></script>
                <script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
                <script type="text/hyperscript" src="/static/greeble/hyperscript/greeble.hyperscript"></script>
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
