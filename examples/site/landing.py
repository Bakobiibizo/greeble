from __future__ import annotations

import asyncio
import itertools
import json
import os
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from html import escape
from pathlib import Path
from string import Template

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8045))

ROOT = Path(__file__).resolve().parents[2]
CPTS = ROOT / "packages" / "greeble_components" / "components"
CORE_ASSETS = ROOT / "packages" / "greeble_core" / "assets" / "css"

MODAL_PARTIAL = (CPTS / "modal" / "templates" / "modal.partial.html").read_text(encoding="utf-8")
DRAWER_PARTIAL = """
<div class="drawer-overlay">
  <button
    class="drawer-backdrop"
    hx-get="/drawer/close"
    hx-target="#drawer-root"
    hx-swap="innerHTML"
    aria-label="Close promotions"
  ></button>
  <aside class="drawer-panel" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
    <header class="drawer-panel__header">
      <h2 id="drawer-title" class="greeble-heading-2">Promotions</h2>
      <button class="greeble-icon-button" aria-label="Close"
              hx-get="/drawer/close" hx-target="#drawer-root" hx-swap="innerHTML">×</button>
    </header>
    <div class="stack">
      <p>Unlock expansion-ready features designed for launch teams.</p>
      <ul class="stack">
        <li><strong>Priority Support:</strong> 24/7 incident routing and shared slack channel.</li>
        <li><strong>Workflow Builders:</strong> Automate approvals and cross-team updates.</li>
        <li><strong>Insights Pack:</strong> Deeper analytics with alerting templates.</li>
      </ul>
      <button class="greeble-button greeble-button--primary" type="button"
              hx-post="/newsletter/subscribe"
              hx-target="#drawer-root"
              hx-swap="none">
        Notify me about upgrades
      </button>
    </div>
  </aside>
</div>
"""

COMPONENT_STYLE_PATHS = [
    CPTS / "button" / "static" / "button.css",
    CPTS / "input" / "static" / "input.css",
    CPTS / "modal" / "static" / "modal.css",
    CPTS / "toast" / "static" / "toast.css",
    CPTS / "table" / "static" / "table.css",
]
COMPONENT_CSS = "\n".join(path.read_text(encoding="utf-8") for path in COMPONENT_STYLE_PATHS)

app = FastAPI(title="Greeble Landing Demo")
app.mount(
    "/static/greeble",
    StaticFiles(directory=str(CORE_ASSETS)),
    name="greeble-static",
)


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    tagline: str
    price: float
    inventory: int
    category: str
    description: str


@dataclass(frozen=True)
class Account:
    org: str
    owner: str
    plan: str
    seats_used: int
    seats_total: int
    status: str


PRODUCTS: tuple[Product, ...] = (
    Product(
        sku="orbit-kit",
        name="Orbit Collaboration Kit",
        tagline="Async-friendly project hub",
        price=24.0,
        inventory=12,
        category="Productivity",
        description=("Curated dashboards, checklists, and alerts for fast-moving launch teams."),
    ),
    Product(
        sku="comet-crm",
        name="Comet CRM",
        tagline="Sales workflow without the drag",
        price=48.0,
        inventory=7,
        category="Sales",
        description=("Pipeline automations plus activity digests for founders selling on the go."),
    ),
    Product(
        sku="lunar-insights",
        name="Lunar Insights",
        tagline="Streaming metrics with narratives",
        price=96.0,
        inventory=4,
        category="Analytics",
        description=("Explainable analytics with alerts for product, growth, and support teams."),
    ),
    Product(
        sku="nova-support",
        name="Nova Support Desk",
        tagline="Reach inbox zero on autopilot",
        price=32.0,
        inventory=18,
        category="Support",
        description=(
            "Context-aware replies, macros, and live status visibility for customer advocates."
        ),
    ),
    Product(
        sku="relay-payments",
        name="Relay Payments",
        tagline="Collect revenue in one click",
        price=64.0,
        inventory=9,
        category="Finance",
        description=("Checkout flows, subscription retries, and finance-ready exports built-in."),
    ),
    Product(
        sku="zen-launchpad",
        name="Zen Launchpad",
        tagline="Personalized onboarding sequences",
        price=28.0,
        inventory=16,
        category="Onboarding",
        description=(
            "Progressive activation checklists with nudges across email, SMS, and in-app."
        ),
    ),
)

_PRODUCTS_BY_SKU = {product.sku: product for product in PRODUCTS}

ACCOUNTS: tuple[Account, ...] = (
    Account(
        org="Orbit Labs",
        owner="ava@orbitlabs.dev",
        plan="Scale",
        seats_used=42,
        seats_total=50,
        status="active",
    ),
    Account(
        org="Nova Civic",
        owner="sam@nova.city",
        plan="Starter",
        seats_used=8,
        seats_total=10,
        status="pending",
    ),
    Account(
        org="Comet Ops",
        owner="lin@cometops.io",
        plan="Enterprise",
        seats_used=110,
        seats_total=120,
        status="delinquent",
    ),
    Account(
        org="Atlas & Co",
        owner="taylor@atlasand.co",
        plan="Scale",
        seats_used=28,
        seats_total=45,
        status="active",
    ),
    Account(
        org="Lumen Growth",
        owner="mira@lumengrowth.io",
        plan="Starter",
        seats_used=6,
        seats_total=12,
        status="pending",
    ),
    Account(
        org="Helio Systems",
        owner="kai@helio.systems",
        plan="Enterprise",
        seats_used=132,
        seats_total=150,
        status="active",
    ),
)

_FEED_COUNTER = itertools.count(1)


def render_page(body_html: str) -> HTMLResponse:
    layout = Template(
        """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Greeble Demo</title>
    <link rel="stylesheet" href="/static/greeble/greeble-core.css" />
    <style>
      :root {
        color-scheme: light dark;
      }
      body {
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell,
          Noto Sans, sans-serif;
        margin: 0;
        background: var(--surface-elevated, #111);
        color: var(--text-primary, #f5f5f5);
      }
      header.site-header {
        padding: 1.5rem clamp(1.5rem, 3vw, 3rem);
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      main.landing {
        padding: clamp(1.5rem, 3vw, 3rem);
        display: grid;
        gap: 2.5rem;
      }
      section.demo {
        display: grid;
        gap: 1.25rem;
        padding: 1.5rem;
        border-radius: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
      }
      section.demo header {
        display: flex;
        flex-direction: column;
        gap: .35rem;
      }
      .cluster {
        display: flex;
        gap: .75rem;
        flex-wrap: wrap;
        align-items: center;
      }
      .stack {
        display: grid;
        gap: .75rem;
      }
      .grid-two {
        display: grid;
        gap: 1.25rem;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      }
      .demo aside, .demo article {
        background: rgba(0, 0, 0, 0.25);
        border-radius: .75rem;
        padding: 1rem;
      }
      .demo-listbox {
        list-style: none;
        padding: 0;
        margin: 0;
        max-height: 14rem;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: .75rem;
      }
      .demo-listbox li[role="option"] {
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      .demo-listbox button {
        background: none;
        width: 100%;
        border: 0;
        color: inherit;
        text-align: left;
        padding: .85rem 1rem;
        cursor: pointer;
      }
      .demo-listbox button:focus-visible {
        outline: 2px solid var(--accent, #93c5fd);
      }
      #greeble-toasts {
        position: fixed;
        inset-inline-end: clamp(1rem, 2vw, 2.5rem);
        inset-block-start: clamp(1rem, 2vw, 2.5rem);
        display: grid;
        gap: .75rem;
        z-index: 999;
      }
      .demo-table-wrapper {
        overflow-x: auto;
      }
      table.greeble-table {
        min-width: 520px;
      }
      /* Modal root and modal element styling */
      #modal-root {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 999; /* above drawer */
      }
      #modal-root > * { pointer-events: auto; }
      #drawer-root {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 998;
      }
      #drawer-root > * {
        pointer-events: auto;
      }
      .drawer-overlay {
        position: fixed;
        inset: 0;
        background: rgba(13, 13, 23, 0.62);
        display: flex;
        justify-content: flex-end;
        align-items: stretch;
      }
      .drawer-backdrop {
        position: absolute;
        inset: 0;
        background: transparent;
        border: 0;
        cursor: pointer;
      }
      .drawer-panel {
        position: relative;
        margin: 0;
        background: rgba(18, 18, 27, 0.95);
        width: min(24rem, 100%);
        padding: 1.5rem;
        display: grid;
        gap: 1rem;
        box-shadow: -12px 0 32px rgba(0, 0, 0, 0.45);
        overflow-y: auto;
      }
      .drawer-panel__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
      }
      .drawer-panel__header .greeble-icon-button {
        background: none;
        border: 0;
        color: inherit;
        font-size: 1.75rem;
        line-height: 1;
        cursor: pointer;
      }
      .newsletter-callout {
        font-size: .95rem;
        color: rgba(255, 255, 255, 0.75);
      }
      .feed-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
      }
$component_css
    </style>
    <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/sse.js" defer></script>
  </head>
  <body>
    <div id="greeble-toasts" aria-live="polite" aria-atomic="false"></div>
    <div id="modal-root" hx-target="this"></div>
    <div id="drawer-root" hx-target="this"></div>
    <header class="site-header">
      <div>
        <h1 class="greeble-heading-1">Launch faster with Greeble</h1>
        <p>
          Every component wired in a realistic flow so product teams can test
          behaviors end-to-end.
        </p>
      </div>
      <a
        class="greeble-button greeble-button--primary"
        href="https://github.com/bakobiibizo/greeble"
        target="_blank"
        rel="noreferrer"
      >
        View Repo
      </a>
    </header>
    <main class="landing">
      $body
    </main>
    <script>
      document.addEventListener('htmx:afterRequest', (event) => {
        const elt = event.detail?.elt;
        if (!elt) return;
        if (elt.matches('[data-tab]')) {
          const current = elt.getAttribute('data-tab');
          document.querySelectorAll('#product-tablist [role="tab"]').forEach((tab) => {
            const isActive = tab.getAttribute('data-tab') === current;
            tab.setAttribute('aria-selected', String(isActive));
            tab.toggleAttribute('data-active', isActive);
          });
        }
      });
    </script>
  </body>
</html>
        """
    )
    return HTMLResponse(layout.substitute(body=body_html, component_css=COMPONENT_CSS))


def build_sign_in_section() -> str:
    initial_group = _render_signin_group("", None, swap_oob=False)
    return f"""
<section class=\"demo\" id=\"sign-in\">
  <header>
    <h2 class=\"greeble-heading-2\">Sign In</h2>
    <p>Access your launch workspace instantly and keep shipping momentum.</p>
  </header>
  <form
    class=\"stack\"
    hx-post=\"/auth/sign-in\"
    hx-target=\"#sign-in-status\"
    hx-swap=\"innerHTML\"
  >
    {initial_group}
    <div class=\"cluster\">
      <button class=\"greeble-button greeble-button--primary\" type=\"submit\">Sign in</button>
      <button class=\"greeble-button greeble-button--secondary\" type=\"button\"
              hx-post=\"/newsletter/subscribe\"
              hx-target=\"#sign-in\"
              hx-swap=\"none\">
        Sign up for newsletter
      </button>
      <button class=\"greeble-button greeble-button--ghost\" type=\"button\"
              hx-get=\"/modal/example\"
              hx-target=\"#modal-root\"
              hx-swap=\"innerHTML\">
        Preview onboarding modal
      </button>
    </div>
  </form>
  <div id=\"sign-in-status\" class=\"newsletter-callout\" aria-live=\"polite\"></div>
</section>
    """


def build_palette_section() -> str:
    default_products = PRODUCTS[:4]
    initial_results = _render_palette_results(default_products)
    initial_detail = _render_palette_detail(PRODUCTS[0]) if PRODUCTS else "<p>No products yet.</p>"
    return f"""
<section class="demo" id="product-search">
  <header>
    <h2 class="greeble-heading-2">Product Search & Command Palette</h2>
    <p>Use keyboard-friendly search to populate a listbox and update the detail preview.</p>
  </header>
  <form class="stack"
        hx-post="/palette/search"
        hx-trigger="submit, keyup changed delay:300ms from:input[name=q]"
        hx-target="#palette-results"
        hx-swap="innerHTML"
        autocomplete="off">
    <label class="greeble-label" for="palette-query">Search the catalog</label>
    <input
      id="palette-query"
      name="q"
      class="greeble-input"
      type="search"
      placeholder="Search by name or category"
    />
  </form>
  <div class="grid-two">
    <div>
      <h3 class="greeble-heading-3">Results</h3>
      <div id="palette-results" role="listbox" aria-label="Product matches">
        {initial_results}
      </div>
    </div>
    <div id="palette-detail" class="stack" aria-live="polite">
      <h3 class="greeble-heading-3">Selection</h3>
      {initial_detail}
    </div>
  </div>
</section>
    """


def build_table_section() -> str:
    table_component = (CPTS / "table" / "templates" / "table.html").read_text(encoding="utf-8")
    return f"""
<section class=\"demo\" id=\"featured-data\">
  <header>
    <h2 class=\"greeble-heading-2\">Featured Data</h2>
    <p>Paginated inventory snapshot with HTMX-driven sorting, search, and exports.</p>
  </header>
  {table_component}
</section>
    """


def build_tabs_section() -> str:
    return """
<section class="demo" id="product-tabs-section">
  <header>
    <h2 class="greeble-heading-2">Product Tabs</h2>
    <p>Lazy-load deeper product content while maintaining accessible tab semantics.</p>
  </header>
  <div class="stack" role="region">
    <div id="product-tablist" class="greeble-tabs" role="tablist">
      <button
        role="tab"
        data-tab="overview"
        aria-selected="true"
        aria-controls="product-tab-panel"
        hx-get="/tabs/overview"
        hx-target="#product-tab-panel"
        hx-swap="innerHTML"
        class="greeble-button greeble-button--ghost"
        data-active
      >
        Overview
      </button>
      <button
        role="tab"
        data-tab="pricing"
        aria-selected="false"
        aria-controls="product-tab-panel"
        hx-get="/tabs/pricing"
        hx-target="#product-tab-panel"
        hx-swap="innerHTML"
        class="greeble-button greeble-button--ghost"
      >
        Pricing
      </button>
      <button
        role="tab"
        data-tab="integrations"
        aria-selected="false"
        aria-controls="product-tab-panel"
        hx-get="/tabs/integrations"
        hx-target="#product-tab-panel"
        hx-swap="innerHTML"
        class="greeble-button greeble-button--ghost"
      >
        Integrations
      </button>
    </div>
    <div
      id="product-tab-panel"
      role="tabpanel"
      aria-live="polite"
      hx-get="/tabs/overview"
      hx-trigger="load"
      hx-target="this"
      hx-swap="innerHTML"
    >
      <p>Loading tab content…</p>
    </div>
  </div>
</section>
    """


def build_drawer_section() -> str:
    return """
<section class="demo" id="promotions">
  <header>
    <h2 class="greeble-heading-2">Promotions Drawer</h2>
    <p>Offer contextual upgrades in a non-blocking side panel.</p>
  </header>
  <button class="greeble-button" hx-get="/drawer/open" hx-target="#drawer-root" hx-swap="innerHTML">
    Open Promotions
  </button>
  <p>
    The drawer returns a partial fragment; clicking the backdrop or close button clears the
    target.
  </p>
</section>
    """


def build_infinite_list_section() -> str:
    return """
<section class="demo" id="infinite-updates">
  <header>
    <h2 class="greeble-heading-2">Infinite Updates</h2>
    <p>Stream activity with both auto-revealed sentinels and manual "Load more" controls.</p>
  </header>
  <ul id="updates-list" class="stack" aria-live="polite">
    <li>Deployment complete — baseline telemetry online.</li>
    <li>Feature flags synced for the beta cohort.</li>
  </ul>
  <div
    id="updates-sentinel"
    hx-get="/list"
    hx-trigger="revealed"
    hx-target="#updates-list"
    hx-swap="beforeend"
  ></div>
  <div class="feed-controls">
    <span>Sentinel appends items when scrolled into view.</span>
    <button class="greeble-button" type="button"
            hx-get="/list"
            hx-target="#updates-list"
            hx-swap="beforeend">
      Load more
    </button>
  </div>
</section>
    """


def build_sse_section() -> str:
    return """
<section class="demo" id="live-status">
  <header>
    <h2 class="greeble-heading-2">Live Status</h2>
    <p>Server-Sent Events push status ticks out-of-band without extra requests.</p>
  </header>
  <div id="live-clock" class="greeble-card">Waiting for server time…</div>
  <div hx-ext="sse" sse-connect="/stream" sse-swap="message"></div>
</section>
    """


@app.get("/", response_class=HTMLResponse)
async def landing() -> HTMLResponse:
    sections = "".join(
        [
            build_sign_in_section(),
            build_palette_section(),
            build_table_section(),
            build_tabs_section(),
            build_drawer_section(),
            build_infinite_list_section(),
            build_sse_section(),
        ]
    )
    return render_page(sections)


@app.get("/modal/example", response_class=HTMLResponse)
async def modal_example() -> HTMLResponse:
    return HTMLResponse(MODAL_PARTIAL)


@app.get("/modal/close", response_class=HTMLResponse)
async def modal_close() -> HTMLResponse:
    return HTMLResponse("")


@app.post("/modal/submit", response_class=HTMLResponse)
async def modal_submit(email: str = Form("")) -> HTMLResponse:
    email = email.strip()
    if not email or "@" not in email:
        toast_html = _toast_fragment(
            "danger",
            "Check email",
            "Enter a valid email to continue.",
        )
        toast = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
        return HTMLResponse(MODAL_PARTIAL + toast, status_code=400)

    toast_html = _toast_fragment(
        "success",
        "Invite sent",
        f"Welcome aboard, {email}!",
    )
    toast_html = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    close_modal = '<div id="modal-root" hx-swap-oob="true"></div>'
    return HTMLResponse(close_modal + toast_html)


@app.post("/newsletter/subscribe", response_class=HTMLResponse)
@app.post("/notify", response_class=HTMLResponse)
async def newsletter_subscribe() -> HTMLResponse:
    toast_html = _toast_fragment("info", "Subscribed", "You're on the launch list.")
    html = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    return HTMLResponse(html)


def _filter_products(query: str) -> Iterable[Product]:
    q = query.lower()
    for product in PRODUCTS:
        haystack = " ".join(
            [product.name, product.category, product.tagline, product.description]
        ).lower()
        if q in haystack:
            yield product


def _render_palette_results(products: Iterable[Product]) -> str:
    items: list[str] = []
    for product in products:
        items.append(
            Template(
                """
<li role=\"option\" data-sku=\"$sku\">
  <button type=\"button\" class=\"greeble-button greeble-button--ghost\"
          hx-post=\"/palette/select\"
          hx-target=\"#palette-detail\"
          hx-swap=\"innerHTML\"
          hx-vals='{"sku": "$sku"}'>
    <strong>$name</strong><br />
    <span>$tagline</span>
  </button>
</li>
                """
            ).substitute(
                sku=escape(product.sku),
                name=escape(product.name),
                tagline=escape(product.tagline),
            )
        )

    if not items:
        return '<p role="status">No results. Try a different name or category.</p>'

    return (
        '<ul class="demo-listbox" role="listbox" aria-label="Matching products">'
        + "".join(items)
        + "</ul>"
    )


def _render_palette_detail(product: Product) -> str:
    return Template(
        """
<article>
  <header>
    <h3 class="greeble-heading-3">$name</h3>
    <p>$tagline</p>
  </header>
  <dl class="stack">
    <div><dt>SKU</dt><dd>$sku</dd></div>
    <div><dt>Category</dt><dd>$category</dd></div>
    <div><dt>Price</dt><dd>$price_fmt</dd></div>
    <div><dt>Inventory</dt><dd>$inventory</dd></div>
  </dl>
  <p>$description</p>
</article>
        """
    ).substitute(
        name=escape(product.name),
        tagline=escape(product.tagline),
        sku=escape(product.sku),
        category=escape(product.category),
        price_fmt=f"${product.price:.2f}/seat",
        inventory=product.inventory,
        description=escape(product.description),
    )


@app.post("/palette/search", response_class=HTMLResponse)
async def palette_search(q: str = Form("")) -> HTMLResponse:
    query = q.strip()
    if not query:
        return HTMLResponse("<p>Type at least one character to search.</p>")

    matches = list(_filter_products(query))
    html = _render_palette_results(matches)
    return HTMLResponse(html)


@app.post("/palette/select", response_class=HTMLResponse)
async def palette_select(sku: str = Form(...)) -> HTMLResponse:
    product = _PRODUCTS_BY_SKU.get(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Unknown product")
    return HTMLResponse(_render_palette_detail(product))


def _sort_accounts(accounts: Iterable[Account], field: str, direction: str) -> list[Account]:
    reverse = direction == "desc"
    key_map = {
        "org": lambda a: a.org.lower(),
        "plan": lambda a: a.plan.lower(),
        "seats": lambda a: a.seats_used / max(1, a.seats_total),
        "status": lambda a: {"active": 0, "pending": 1, "delinquent": 2}.get(a.status, 3),
    }
    key = key_map.get(field, key_map["org"])
    return sorted(accounts, key=key, reverse=reverse)


def _query_accounts(page: int, field: str, direction: str, page_size: int = 3) -> list[Account]:
    sorted_accounts = _sort_accounts(ACCOUNTS, field, direction)
    start = (page - 1) * page_size
    end = start + page_size
    return sorted_accounts[start:end]


def _status_display(account: Account) -> tuple[str, str]:
    labels = {
        "active": ("greeble-table__status--active", "Active"),
        "pending": ("greeble-table__status--pending", "Pending"),
        "delinquent": ("greeble-table__status--delinquent", "Delinquent"),
    }
    return labels.get(account.status, ("", account.status.title()))


def _account_slug(account: Account) -> str:
    return account.org.lower().replace(" & ", "-").replace(" ", "-")


def _render_account_rows(accounts: Iterable[Account]) -> str:
    rows: list[str] = []
    for account in accounts:
        status_class, status_label = _status_display(account)
        slug = _account_slug(account)
        seats = f"{account.seats_used} / {account.seats_total}"

        if account.status == "pending":
            secondary_action = (
                '<button class="greeble-button greeble-button--ghost" type="button"\n'
                f'        hx-post="/table/accounts/{slug}/remind"\n'
                '        hx-target="#table-body"\n'
                '        hx-swap="none">Send reminder</button>'
            )
        elif account.status == "delinquent":
            secondary_action = (
                '<button class="greeble-button greeble-button--destructive" type="button"\n'
                f'        hx-post="/table/accounts/{slug}/escalate"\n'
                '        hx-target="#table-body"\n'
                '        hx-swap="none">Escalate</button>'
            )
        else:
            secondary_action = (
                '<button class="greeble-button greeble-button--ghost" type="button"\n'
                f'        hx-delete="/table/accounts/{slug}"\n'
                '        hx-target="closest tr"\n'
                '        hx-swap="outerHTML">Archive</button>'
            )

        rows.append(
            Template(
                """
<tr>
  <th scope="row">
    <div class="greeble-table__primary">$org</div>
    <p class="greeble-table__meta">Owner: $owner</p>
  </th>
  <td>$plan</td>
  <td>$seats</td>
  <td>
    <span class="greeble-table__status $status_class">
      <span aria-hidden="true">●</span>
      $status_label
    </span>
  </td>
  <td class="greeble-table__actions">
    <button class="greeble-button greeble-button--ghost" type="button"
            hx-get="/table/accounts/$slug"
            hx-target="#table-body"
            hx-swap="none">
      View
    </button>
    $secondary_action
  </td>
</tr>
                """
            ).substitute(
                org=escape(account.org),
                owner=escape(account.owner),
                plan=escape(account.plan),
                seats=seats,
                status_class=status_class,
                status_label=status_label,
                slug=escape(slug),
                secondary_action=secondary_action,
            )
        )

    return "".join(rows)


_ACCOUNTS_BY_SLUG = {_account_slug(account): account for account in ACCOUNTS}


def _get_account_by_slug(slug: str) -> Account:
    try:
        return _ACCOUNTS_BY_SLUG[slug]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Unknown account") from exc


def _filter_accounts(query: str) -> list[Account]:
    term = query.lower()
    return [
        account
        for account in ACCOUNTS
        if term in account.org.lower()
        or term in account.owner.lower()
        or term in account.plan.lower()
    ]


def _toast_fragment(level: str, title: str, message: str, *, icon: str | None = None) -> str:
    icons = {
        "success": "✔",
        "info": "ℹ",
        "warn": "!",
        "danger": "✖",
    }
    symbol = icon if icon is not None else icons.get(level, "ℹ")
    return Template(
        """
  <div class="greeble-toast greeble-toast--$level" role="status" data-level="$level">
    <div class="greeble-toast__icon" aria-hidden="true">$icon</div>
    <div class="greeble-toast__body">
      <p class="greeble-toast__title">$title</p>
      <p class="greeble-toast__message">$message</p>
    </div>
    <button
      class="greeble-icon-button greeble-toast__dismiss"
      type="button"
      aria-label="Dismiss notification"
      hx-get="/toast/dismiss"
      hx-target="closest .greeble-toast"
      hx-swap="outerHTML"
    >
      ×
    </button>
  </div>
        """
    ).substitute(
        level=escape(level),
        title=escape(title),
        message=escape(message),
        icon=escape(symbol),
    )


@app.get("/table", response_class=HTMLResponse)
async def table_rows(request: Request) -> HTMLResponse:
    params = request.query_params
    page = int(params.get("page", 1))
    sort_param = params.get("sort", "org:asc")
    field, _, direction = sort_param.partition(":")
    direction = direction or "asc"

    rows = _query_accounts(page, field, direction)

    if not rows:
        return HTMLResponse('<tr><td colspan="5">No matching accounts.</td></tr>')

    payload = json.dumps({"greeble:table:update": {"page": page, "sort": f"{field}:{direction}"}})
    headers = {"HX-Trigger": payload}
    return HTMLResponse(_render_account_rows(rows), headers=headers)


@app.post("/table/search", response_class=HTMLResponse)
async def table_search(q: str = Form("")) -> HTMLResponse:
    query = q.strip()
    if not query:
        rows = _query_accounts(1, "org", "asc")
        html = _render_account_rows(rows)
        headers = {"HX-Trigger": json.dumps({"greeble:table:update": {"query": ""}})}
        return HTMLResponse(html, headers=headers)

    matches = _filter_accounts(query)
    if not matches:
        return HTMLResponse('<tr><td colspan="5">No accounts match this search.</td></tr>')

    headers = {
        "HX-Trigger": json.dumps(
            {"greeble:table:update": {"query": query, "results": len(matches)}}
        )
    }
    return HTMLResponse(_render_account_rows(matches), headers=headers)


@app.post("/table/export", response_class=HTMLResponse)
async def table_export() -> HTMLResponse:
    toast_html = _toast_fragment(
        "info",
        "Export queued",
        "We emailed a CSV of active accounts to ops@orbitlabs.dev.",
    )
    body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    headers = {"HX-Trigger": json.dumps({"greeble:toast": {"level": "info"}})}
    return HTMLResponse(body, headers=headers)


@app.get("/table/accounts/{slug}", response_class=HTMLResponse)
async def table_account_view(slug: str) -> HTMLResponse:
    account = _get_account_by_slug(slug)
    toast_html = _toast_fragment(
        "info",
        "Account opened",
        f"Viewing metrics for {account.org}.",
    )
    body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    headers = {
        "HX-Trigger": json.dumps({"greeble:table:view": {"org": account.org}}),
    }
    return HTMLResponse(body, headers=headers)


@app.post("/table/accounts/{slug}/remind", response_class=HTMLResponse)
async def table_account_remind(slug: str) -> HTMLResponse:
    account = _get_account_by_slug(slug)
    toast_html = _toast_fragment(
        "warn",
        "Reminder sent",
        f"Queued a payment reminder to {account.owner}.",
    )
    body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    headers = {
        "HX-Trigger": json.dumps({"greeble:table:remind": {"org": account.org}}),
    }
    return HTMLResponse(body, headers=headers)


@app.post("/table/accounts/{slug}/escalate", response_class=HTMLResponse)
async def table_account_escalate(slug: str) -> HTMLResponse:
    account = _get_account_by_slug(slug)
    toast_html = _toast_fragment(
        "danger",
        "Escalation logged",
        f"Finance will follow up with {account.org} within the hour.",
    )
    body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    headers = {
        "HX-Trigger": json.dumps({"greeble:table:escalate": {"org": account.org}}),
    }
    return HTMLResponse(body, headers=headers)


@app.delete("/table/accounts/{slug}", response_class=HTMLResponse)
async def table_account_archive(slug: str) -> HTMLResponse:
    account = _get_account_by_slug(slug)
    toast_html = _toast_fragment(
        "info",
        "Archived",
        f"{account.org} moved to the archived list.",
    )
    body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    headers = {
        "HX-Trigger": json.dumps({"greeble:table:archive": {"org": account.org}}),
    }
    # Empty response (aside from OOB toast) removes the archived row
    return HTMLResponse(body, headers=headers)


@app.get("/toast/dismiss", response_class=HTMLResponse)
async def toast_dismiss() -> HTMLResponse:
    return HTMLResponse("")


@app.get("/tabs/{tab_key}", response_class=HTMLResponse)
async def load_tab(tab_key: str) -> HTMLResponse:
    content_map = {
        "overview": (
            "<p>Consolidate launches, async updates, and approvals in a single mission control.</p>"
        ),
        "pricing": (
            "<p>Usage-based pricing starts at $24/month with volume discounts after 50 seats.</p>"
        ),
        "integrations": (
            '<ul class="stack"><li>Slack + Teams alerts</li><li>Linear issues sync</li>'
            "<li>Segment + RudderStack events</li></ul>"
        ),
    }
    html = content_map.get(tab_key)
    if not html:
        raise HTTPException(status_code=404, detail="Unknown tab")
    return HTMLResponse(html)


@app.get("/drawer/open", response_class=HTMLResponse)
async def drawer_open() -> HTMLResponse:
    return HTMLResponse(DRAWER_PARTIAL)


@app.get("/drawer/close", response_class=HTMLResponse)
async def drawer_close() -> HTMLResponse:
    return HTMLResponse("")


def _render_signin_group(email: str, error: str | None, *, swap_oob: bool) -> str:
    classes = ["greeble-field"]
    if error:
        classes.append("greeble-field--invalid")

    attrs = [
        'id="signin-email-group"',
        f'class="{" ".join(classes)}"',
        'hx-post="/auth/validate"',
        (
            'hx-trigger="change from:#signin-email, keyup delay:500ms '
            'from:#signin-email, blur from:#signin-email"'
        ),
        'hx-target="#signin-email-group"',
        'hx-swap="outerHTML"',
        'hx-include="#signin-email"',
    ]
    if swap_oob:
        attrs.append('hx-swap-oob="true"')

    described_by = ["signin-hint"]
    input_attrs = [
        'id="signin-email"',
        'name="email"',
        'type="email"',
        'class="greeble-input"',
        'autocomplete="email"',
        "required",
    ]
    if email:
        input_attrs.append(f'value="{escape(email, quote=True)}"')
    if error:
        input_attrs.append('aria-invalid="true"')
        described_by.append("signin-error")
    described = " ".join(described_by)
    input_attrs.append(f'aria-describedby="{escape(described, quote=True)}"')

    error_html = (
        f'<p id="signin-error" class="greeble-field__error" role="alert">{escape(error)}</p>'
        if error
        else ""
    )

    return Template(
        """
<div $attrs>
  <label class="greeble-field__label" for="signin-email">Work email</label>
  <input $input_attrs />
  <p id="signin-hint" class="greeble-field__hint">We'll email you a magic link.</p>
  $error_html
</div>
        """
    ).substitute(
        attrs=" ".join(attrs),
        input_attrs=" ".join(input_attrs),
        error_html=error_html,
    )


def _validate_signin_email(email: str) -> str | None:
    value = email.strip()
    if not value:
        return "Email is required to sign in."
    if "@" not in value or value.startswith("@") or value.endswith("@"):
        return "Enter a valid work email address."
    return None


@app.post("/auth/validate", response_class=HTMLResponse)
async def auth_validate(email: str = Form("")) -> HTMLResponse:
    error = _validate_signin_email(email)
    html = _render_signin_group(email, error, swap_oob=False)
    status = 400 if error else 200
    return HTMLResponse(html, status_code=status)


@app.post("/auth/sign-in", response_class=HTMLResponse)
async def auth_sign_in(email: str = Form("")) -> HTMLResponse:
    error = _validate_signin_email(email)
    if error:
        group_html = _render_signin_group(email, error, swap_oob=True)
        status_area = '<div id="sign-in-status">Fix the highlighted field to continue.</div>'
        return HTMLResponse(group_html + status_area, status_code=400)

    reset_group = _render_signin_group("", None, swap_oob=True)
    toast_html = _toast_fragment(
        "success",
        "Signed in",
        f"Signed in as {email.strip()}.",
    )
    toast_html = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    status_area = '<div id="sign-in-status">We sent a magic link to your inbox.</div>'
    return HTMLResponse(reset_group + toast_html + status_area)


@app.get("/list", response_class=HTMLResponse)
async def infinite_list() -> HTMLResponse:
    items = []
    for _ in range(3):
        idx = next(_FEED_COUNTER)
        items.append(f"<li>Update #{idx}: Background job completed.</li>")
    return HTMLResponse("".join(items))


async def _clock_stream(test_mode: bool) -> AsyncIterator[str]:
    yield ": open\n\n"
    now = asyncio.get_running_loop().time()
    fragment = f'<div id="live-clock" hx-swap-oob="true">Server time tick: {now:.0f}</div>'
    yield f"data: {fragment}\n\n"
    if test_mode:
        return
    while True:
        await asyncio.sleep(2)
        now = asyncio.get_running_loop().time()
        fragment = f'<div id="live-clock" hx-swap-oob="true">Server time tick: {now:.0f}</div>'
        yield f"data: {fragment}\n\n"


@app.get("/stream")
async def sse_stream(request: Request) -> StreamingResponse:
    test_mode = request.headers.get("x-test") == "1" or request.query_params.get("test") == "1"
    return StreamingResponse(
        _clock_stream(test_mode),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.site.landing:app", host=str(HOST), port=int(PORT), reload=True)
