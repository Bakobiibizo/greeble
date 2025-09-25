from __future__ import annotations

import itertools
import json
from collections.abc import Iterable
from dataclasses import dataclass
from html import escape
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from greeble.demo import (
    filter_products,
    load_project_component_template,
    render_palette_detail,
    render_palette_results,
    render_valid_email_group,
    toast_block,
    toast_fragment,
    validate_signin_email,
)
from greeble.demo import (
    table_rows as render_table_rows,
)
from greeble.demo.helpers import ProductLike

# Project root when this file is located at src/greeble_starter/app.py
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app = FastAPI(title="Greeble Starter")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@dataclass
class Product:
    sku: str
    name: str
    tagline: str
    price: float
    inventory: int
    category: str
    description: str


PRODUCTS: tuple[Product, ...] = (
    Product(
        sku="orbit-kit",
        name="Orbit Collaboration Kit",
        tagline="Async-friendly project hub",
        price=24.0,
        inventory=12,
        category="Productivity",
        description="Dashboards, checklists, and alerts for launch teams.",
    ),
    Product(
        sku="comet-crm",
        name="Comet CRM",
        tagline="Sales workflow without the drag",
        price=48.0,
        inventory=7,
        category="Sales",
        description="Pipeline automations plus activity digests.",
    ),
    Product(
        sku="nova-support",
        name="Nova Support Desk",
        tagline="Reach inbox zero on autopilot",
        price=32.0,
        inventory=18,
        category="Support",
        description="Context-aware replies and live status visibility.",
    ),
)

_PRODUCTS_BY_SKU = {product.sku: product for product in PRODUCTS}


@dataclass
class Account:
    org: str
    owner: str
    plan: str
    seats_used: int
    seats_total: int
    status: str


ACCOUNTS: tuple[Account, ...] = (
    Account("Orbit Labs", "ava@orbitlabs.dev", "Scale", 42, 50, "active"),
    Account("Nova Civic", "sam@nova.city", "Starter", 8, 10, "pending"),
    Account("Comet Ops", "lin@cometops.io", "Enterprise", 110, 120, "delinquent"),
)

_FEED_COUNTER = itertools.count(1)
FEED_MESSAGES = (
    "Background job completed successfully.",
    "Status page updated for customers.",
    "Webhook delivered to analytics partner.",
)

_TAB_CONTENT = {
    "overview": {
        "title": "Mission control",
        "description": "Consolidate launches and approvals in one workspace.",
        "items": [
            "Track blockers and owners in real time.",
            "Broadcast status updates to stakeholders.",
            "Pipe alerts to Slack, Teams, and email.",
        ],
    },
    "pricing": {
        "title": "Usage-based pricing",
        "description": "Volume discounts unlock after 50 seats.",
        "items": [
            "Starter tier includes 10 seats for $24/month.",
            "Scale tier adds workflow automation and analytics.",
            "Enterprise tier includes SSO, audit logs, and 24/7 support.",
        ],
    },
    "integrations": {
        "title": "Integrations",
        "description": "Connect launch tooling in a few clicks.",
        "items": [
            "Slack & Teams updates for announcements.",
            "Linear issue syncing for launch blockers.",
            "Segment and RudderStack event streaming.",
        ],
    },
}

_STEPPER_STEPS = {
    "plan": {
        "title": "Plan launch",
        "description": "Confirm timeline, owners, and messaging.",
        "tasks": [
            "Align on launch date and success metrics.",
            "Draft internal enablement notes.",
            "Schedule dry run with support and marketing.",
        ],
        "prev": None,
        "next": "enable",
    },
    "enable": {
        "title": "Enable teams",
        "description": "Share launch briefs and escalation paths.",
        "tasks": [
            "Distribute go-live checklist to stakeholders.",
            "Update support macros and status responses.",
            "Confirm metrics dashboard owners.",
        ],
        "prev": "plan",
        "next": "launch",
    },
    "launch": {
        "title": "Go live",
        "description": "Monitor rollout and communicate status.",
        "tasks": [
            "Monitor health metrics and alert thresholds.",
            "Post launch status to customers and partners.",
            "Collect feedback for the retro.",
        ],
        "prev": "enable",
        "next": None,
    },
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return TEMPLATES.TemplateResponse("index.html", {"request": request})


@app.get("/modal/example", response_class=HTMLResponse)
async def modal_example() -> HTMLResponse:
    return HTMLResponse(_component_template("modal.partial.html"))


@app.get("/modal/close", response_class=HTMLResponse)
async def modal_close() -> HTMLResponse:
    return HTMLResponse("")


@app.post("/modal/submit", response_class=HTMLResponse)
async def modal_submit(email: str = Form("")) -> HTMLResponse:
    value = email.strip()
    if not value or "@" not in value:
        toast = toast_fragment("danger", "Try again", "Enter a valid email address.")
        body = _component_template("modal.partial.html") + toast_block(toast)
        return HTMLResponse(body, status_code=400)

    toast = toast_fragment("success", "Invite sent", f"Welcome aboard, {escape(value)}!")
    close = '<div id="modal-root" hx-swap-oob="true"></div>'
    return HTMLResponse(close + toast_block(toast))


@app.post("/palette/search", response_class=HTMLResponse)
async def palette_search(q: str = Form("")) -> HTMLResponse:
    query = q.strip()
    matches = filter_products(PRODUCTS, query) if query else list(PRODUCTS)
    html = _palette_search(matches)
    headers = {"HX-Trigger": json.dumps({"greeble:palette:results": {"count": len(matches)}})}
    return HTMLResponse(html, headers=headers)


@app.post("/palette/select", response_class=HTMLResponse)
async def palette_select(sku: str = Form(...)) -> HTMLResponse:
    product = _PRODUCTS_BY_SKU.get(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Unknown product")
    detail_html = _palette_select(product)
    headers = {"HX-Trigger": json.dumps({"greeble:palette:select": {"sku": sku}})}
    return HTMLResponse(detail_html, headers=headers)


@app.get("/drawer/open", response_class=HTMLResponse)
async def drawer_open() -> HTMLResponse:
    return HTMLResponse(_component_template("drawer.partial.html"))


@app.get("/drawer/close", response_class=HTMLResponse)
async def drawer_close() -> HTMLResponse:
    return HTMLResponse("")


@app.post("/drawer/subscribe", response_class=HTMLResponse)
async def drawer_subscribe(email: str = Form("")) -> HTMLResponse:
    value = email.strip()
    if not value or "@" not in value:
        toast = toast_fragment("danger", "Try again", "Enter a valid work email.")
        return HTMLResponse(toast_block(toast), status_code=400)

    toast = toast_fragment("success", "Walkthrough requested", "We'll follow up shortly.")
    body = '<div id="drawer-root" hx-swap-oob="true"></div>' + toast_block(toast)
    return HTMLResponse(body)


@app.post("/form/validate", response_class=HTMLResponse)
async def form_validate(email: str = Form("")) -> HTMLResponse:
    if validate_signin_email(email):
        return HTMLResponse(_component_template("form.partial.html"), status_code=400)
    return HTMLResponse(_form_valid_group(email, swap_oob=False))


@app.post("/form/submit", response_class=HTMLResponse)
async def form_submit(email: str = Form("")) -> HTMLResponse:
    if validate_signin_email(email):
        return HTMLResponse(_component_template("form.partial.html"), status_code=400)
    toast = toast_fragment("success", "Request received", "We'll reach out soon.")
    body = (
        _form_valid_group("", swap_oob=True)
        + toast_block(toast)
        + '<div id="form-status">Thanks! Check your inbox shortly.</div>'
    )
    return HTMLResponse(body)


@app.get("/table", response_class=HTMLResponse)
async def table_rows(request: Request) -> HTMLResponse:
    page = int(request.query_params.get("page", 1))
    sort = request.query_params.get("sort", "org:asc")
    field, _, direction = sort.partition(":")
    rows = _table_rows(page=page, field=field or "org", direction=direction or "asc")
    headers = {"HX-Trigger": json.dumps({"greeble:table:update": {"page": page, "sort": sort}})}
    return HTMLResponse(rows, headers=headers)


@app.get("/tabs/{tab_key}", response_class=HTMLResponse)
async def load_tab(tab_key: str) -> HTMLResponse:
    data = _TAB_CONTENT.get(tab_key)
    if not data:
        raise HTTPException(status_code=404, detail="Unknown tab")
    items = "\n".join(f"    <li>{escape(item)}</li>" for item in data["items"])
    html = (
        f'<section class="greeble-tabs__content" data-tab="{escape(tab_key)}">'
        f'<h3 class="greeble-heading-3">{escape(str(data["title"]))}</h3>'
        f"<ul>{items}</ul>"
        f"</section>"
    )
    return HTMLResponse(html)


def _component_template(filename: str) -> str:
    return load_project_component_template(BASE_DIR, filename)


def _palette_search(products: Iterable[ProductLike]) -> str:
    return render_palette_results(products)


def _palette_select(product: ProductLike) -> str:
    return render_palette_detail(product)


def _form_valid_group(email: str, *, swap_oob: bool) -> str:
    return render_valid_email_group(email, swap_oob=swap_oob)


def _table_rows(*, page: int, field: str, direction: str) -> str:
    return render_table_rows(
        ACCOUNTS,
        page=page,
        field=field,
        direction=direction or "asc",
    )
