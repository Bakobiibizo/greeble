from __future__ import annotations

import asyncio
import itertools
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

MODAL_PARTIAL = (CPTS / "modal" / "templates" / "modal.partial.html").read_text(
    encoding="utf-8"
)
DRAWER_PARTIAL = """
<div class="drawer-overlay">
  <button class="drawer-backdrop" hx-get="/drawer/close" hx-target="#drawer-root" hx-swap="innerHTML" aria-label="Close promotions"></button>
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
      <button class="greeble-button greeble-button--accent" type="button"
              hx-post="/newsletter/subscribe"
              hx-target="#drawer-root"
              hx-swap="none">
        Notify me about upgrades
      </button>
    </div>
  </aside>
</div>
"""

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


PRODUCTS: tuple[Product, ...] = (
    Product(
        sku="orbit-kit",
        name="Orbit Collaboration Kit",
        tagline="Async-friendly project hub",
        price=24.0,
        inventory=12,
        category="Productivity",
        description="Curated dashboards, checklists, and alerts for fast-moving launch teams.",
    ),
    Product(
        sku="comet-crm",
        name="Comet CRM",
        tagline="Sales workflow without the drag",
        price=48.0,
        inventory=7,
        category="Sales",
        description="Pipeline automations plus activity digests for founders selling on the go.",
    ),
    Product(
        sku="lunar-insights",
        name="Lunar Insights",
        tagline="Streaming metrics with narratives",
        price=96.0,
        inventory=4,
        category="Analytics",
        description="Explainable analytics with alerts for product, growth, and support teams.",
    ),
    Product(
        sku="nova-support",
        name="Nova Support Desk",
        tagline="Reach inbox zero on autopilot",
        price=32.0,
        inventory=18,
        category="Support",
        description="Context-aware replies, macros, and live status visibility for customer advocates.",
    ),
    Product(
        sku="relay-payments",
        name="Relay Payments",
        tagline="Collect revenue in one click",
        price=64.0,
        inventory=9,
        category="Finance",
        description="Checkout flows, subscription retries, and finance-ready exports built-in.",
    ),
    Product(
        sku="zen-launchpad",
        name="Zen Launchpad",
        tagline="Personalized onboarding sequences",
        price=28.0,
        inventory=16,
        category="Onboarding",
        description="Progressive activation checklists with nudges across email, SMS, and in-app.",
    ),
)

_PRODUCTS_BY_SKU = {product.sku: product for product in PRODUCTS}

_TABLE_COLUMNS = (
    ("name", "Product"),
    ("category", "Category"),
    ("price", "Price"),
    ("inventory", "Inventory"),
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
      /* Support both class and id for robustness */
      .greeble-modal, #greeble-modal {
        position: fixed;
        inset: 0;
        display: grid;
        place-items: center;
        z-index: 1000;
      }
      .greeble-modal__backdrop {
        position: absolute;
        inset: 0;
        background: rgba(13, 13, 23, 0.62);
      }
      .greeble-modal__panel {
        position: relative;
        background: rgba(18, 18, 27, 0.98);
        color: inherit;
        padding: 1.25rem;
        width: min(32rem, 92vw);
        border-radius: .85rem;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5);
        display: grid;
        gap: 1rem;
        box-sizing: border-box;
        margin: 0 auto;
      }
      .greeble-modal__header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
      }
      .greeble-modal__header .greeble-icon-button {
        background: none;
        border: 0;
        color: inherit;
        font-size: 1.5rem;
        line-height: 1;
        cursor: pointer;
      }
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
      .newsletter-field,
      .signin-field {
        position: relative;
      }
      .newsletter-error {
        color: #fca5a5;
      }
      .newsletter-hint {
        color: rgba(255, 255, 255, 0.6);
        font-size: .8rem;
      }
      .feed-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
      }
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
        <p>Every component wired in a realistic flow so product teams can test behaviors end-to-end.</p>
      </div>
      <a class="greeble-button greeble-button--accent" href="https://github.com/bakobiibizo/greeble" target="_blank" rel="noreferrer">View Repo</a>
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
    return HTMLResponse(layout.substitute(body=body_html))


def build_sign_in_section() -> str:
    return """
<section class="demo" id="sign-in">
  <header>
    <h2 class="greeble-heading-2">Sign In</h2>
    <p>Access your launch workspace instantly and keep shipping momentum.</p>
  </header>
  <form class="stack" hx-post="/auth/sign-in" hx-target="#sign-in-status" hx-swap="innerHTML">
    <div id="signin-email-group"
         class="stack signin-field"
         hx-post="/auth/validate"
         hx-trigger="change from:#signin-email, keyup delay:500ms from:#signin-email, blur from:#signin-email"
         hx-target="#signin-email-group"
         hx-swap="outerHTML"
         hx-include="#signin-email">
      <label class="greeble-label" for="signin-email">Work email</label>
      <input id="signin-email" name="email" type="email" class="greeble-input" aria-describedby="signin-hint" required />
      <p id="signin-hint" class="newsletter-hint">We'll send a magic link if you don't already have an account.</p>
    </div>
    <div class="cluster">
      <button class="greeble-button greeble-button--accent" type="submit">Sign in</button>
      <button class="greeble-button" type="button"
              hx-post="/newsletter/subscribe"
              hx-target="#sign-in"
              hx-swap="none">
        Sign up for newsletter
      </button>
      <button class="greeble-button greeble-button--ghost" type="button"
              hx-get="/modal/example"
              hx-target="#modal-root"
              hx-swap="innerHTML">
        Preview onboarding modal
      </button>
    </div>
  </form>
  <div id="sign-in-status" class="newsletter-callout" aria-live="polite"></div>
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
    <input id="palette-query" name="q" class="greeble-input" type="search" placeholder="Search by name or category" />
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
    header_cells = []
    for field, label in _TABLE_COLUMNS:
        asc_href = f"/table?page=1&sort={field}:asc"
        desc_href = f"/table?page=1&sort={field}:desc"
        header_cells.append(
            f"""
      <th scope=\"col\">
        <div class=\"cluster\">
          <span>{label}</span>
          <button type=\"button\"
                  class=\"greeble-button greeble-button--ghost\"
                  hx-get=\"{asc_href}\"
                  hx-target=\"#featured-table-body\"
                  hx-swap=\"innerHTML\">
            ↑
          </button>
          <button type=\"button\"
                  class=\"greeble-button greeble-button--ghost\"
                  hx-get=\"{desc_href}\"
                  hx-target=\"#featured-table-body\"
                  hx-swap=\"innerHTML\">
            ↓
          </button>
        </div>
      </th>
            """
        )
    header_html = "".join(header_cells)
    return f"""
<section class=\"demo\" id=\"featured-data\">\n  <header>\n    <h2 class=\"greeble-heading-2\">Featured Data</h2>\n    <p>Paginated inventory snapshot with sortable headers backed by HTMX fragments.</p>\n  </header>\n  <div class=\"demo-table-wrapper\">\n    <table class=\"greeble-table\">\n      <caption>Inventory Overview</caption>\n      <thead>\n        <tr>\n{header_html}\n        </tr>\n      </thead>\n      <tbody id=\"featured-table-body\"\n             hx-get=\"/table?page=1\"\n             hx-trigger=\"load\"\n             hx-swap=\"innerHTML\"></tbody>\n    </table>\n  </div>\n  <nav class=\"greeble-pagination\" aria-label=\"Pagination\">\n    <button class=\"greeble-button\" type=\"button\"\n            hx-get=\"/table?page=1\"\n            hx-target=\"#featured-table-body\"\n            hx-swap=\"innerHTML\">Page 1</button>\n    <button class=\"greeble-button\" type=\"button\"\n            hx-get=\"/table?page=2\"\n            hx-target=\"#featured-table-body\"\n            hx-swap=\"innerHTML\">Page 2</button>\n  </nav>\n</section>\n    """


def build_tabs_section() -> str:
    return """
<section class="demo" id="product-tabs-section">
  <header>
    <h2 class="greeble-heading-2">Product Tabs</h2>
    <p>Lazy-load deeper product content while maintaining accessible tab semantics.</p>
  </header>
  <div class="stack" role="region">
    <div id="product-tablist" class="greeble-tabs" role="tablist">
      <button role="tab" data-tab="overview" aria-selected="true" aria-controls="product-tab-panel"
              hx-get="/tabs/overview" hx-target="#product-tab-panel" hx-swap="innerHTML"
              class="greeble-button greeble-button--ghost" data-active>
        Overview
      </button>
      <button role="tab" data-tab="pricing" aria-selected="false" aria-controls="product-tab-panel"
              hx-get="/tabs/pricing" hx-target="#product-tab-panel" hx-swap="innerHTML"
              class="greeble-button greeble-button--ghost">
        Pricing
      </button>
      <button role="tab" data-tab="integrations" aria-selected="false" aria-controls="product-tab-panel"
              hx-get="/tabs/integrations" hx-target="#product-tab-panel" hx-swap="innerHTML"
              class="greeble-button greeble-button--ghost">
        Integrations
      </button>
    </div>
    <div id="product-tab-panel" role="tabpanel" aria-live="polite"
         hx-get="/tabs/overview" hx-trigger="load" hx-target="this" hx-swap="innerHTML">
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
  <p>The drawer returns a partial fragment; clicking the backdrop or close button clears the target.</p>
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
  <div id="updates-sentinel" hx-get="/list" hx-trigger="revealed" hx-target="#updates-list" hx-swap="beforeend"></div>
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
        toast = (
            '<div id="greeble-toasts" hx-swap-oob="true">'
            '<div class="greeble-toast greeble-toast--danger" role="status">'
            "Enter a valid email to continue."
            "</div></div>"
        )
        return HTMLResponse(MODAL_PARTIAL + toast, status_code=400)

    toast_html = Template(
        """
<div id="greeble-toasts" hx-swap-oob="true">
  <div class="greeble-toast greeble-toast--success" role="status">Welcome aboard, $email!</div>
</div>
        """
    ).substitute(email=escape(email))
    close_modal = '<div id="modal-root" hx-swap-oob="true"></div>'
    return HTMLResponse(close_modal + toast_html)


@app.post("/newsletter/subscribe", response_class=HTMLResponse)
@app.post("/notify", response_class=HTMLResponse)
async def newsletter_subscribe() -> HTMLResponse:
    html = (
        '<div id="greeble-toasts" hx-swap-oob="true">'
        '<div class="greeble-toast greeble-toast--info" role="status">Subscribed to launch updates.</div>'
        "</div>"
    )
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
        return "<p role=\"status\">No results. Try a different name or category.</p>"

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


def _sort_products(products: Iterable[Product], field: str, direction: str) -> list[Product]:
    reverse = direction == "desc"
    key_map = {
        "name": lambda p: p.name.lower(),
        "category": lambda p: p.category.lower(),
        "price": lambda p: p.price,
        "inventory": lambda p: p.inventory,
    }
    key = key_map.get(field, key_map["name"])
    return sorted(products, key=key, reverse=reverse)


def _query_products(page: int, field: str, direction: str, page_size: int = 3) -> list[Product]:
    sorted_products = _sort_products(PRODUCTS, field, direction)
    start = (page - 1) * page_size
    end = start + page_size
    return sorted_products[start:end]


@app.get("/table", response_class=HTMLResponse)
async def table_rows(request: Request) -> HTMLResponse:
    params = request.query_params
    page = int(params.get("page", 1))
    sort_param = params.get("sort", "name:asc")
    field, _, direction = sort_param.partition(":")
    direction = direction or "asc"

    rows = _query_products(page, field, direction)

    if not rows:
        return HTMLResponse('<tr><td colspan="4">No results for this page.</td></tr>')

    cells = []
    for product in rows:
        cells.append(
            Template(
                """
<tr>
  <th scope=\"row\">$name</th>
  <td>$category</td>
  <td>$price_fmt</td>
  <td>$inventory</td>
</tr>
                """
            ).substitute(
                name=escape(product.name),
                category=escape(product.category),
                price_fmt=f"${product.price:.2f}",
                inventory=product.inventory,
            )
        )

    headers = {"HX-Trigger": "featured-table-updated"}
    return HTMLResponse("".join(cells), headers=headers)


@app.get("/tabs/{tab_key}", response_class=HTMLResponse)
async def load_tab(tab_key: str) -> HTMLResponse:
    content_map = {
        "overview": "<p>Consolidate launches, async updates, and approvals in a single mission control.</p>",
        "pricing": "<p>Usage-based pricing starts at $24/month with volume discounts after 50 seats.</p>",
        "integrations": "<ul class=\"stack\"><li>Slack + Teams alerts</li><li>Linear issues sync</li><li>Segment + RudderStack events</li></ul>",
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
    attrs = [
        'id="signin-email-group"',
        'class="stack signin-field"',
        'hx-post="/auth/validate"',
        'hx-trigger="change from:#signin-email, keyup delay:500ms from:#signin-email, blur from:#signin-email"',
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
        'required',
    ]
    if email:
        input_attrs.append(f'value="{escape(email, quote=True)}"')
    if error:
        input_attrs.append('aria-invalid="true"')
        described_by.append("signin-error")
    described = " ".join(described_by)
    input_attrs.append(f'aria-describedby="{escape(described, quote=True)}"')

    error_html = (
        f'<p id="signin-error" class="newsletter-error">{escape(error)}</p>'
        if error
        else ""
    )

    return Template(
        """
<div $attrs>
  <label class="greeble-label" for="signin-email">Work email</label>
  <input $input_attrs />
  <p id="signin-hint" class="newsletter-hint">We'll email you a magic link.</p>
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
    toast_html = Template(
        """
<div id="greeble-toasts" hx-swap-oob="true">
  <div class="greeble-toast greeble-toast--success" role="status">Signed in as $email.</div>
</div>
        """
    ).substitute(email=escape(email.strip()))
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
