from __future__ import annotations

import asyncio
import itertools
import json
import os
from collections.abc import AsyncIterator, Iterable, Iterator
from dataclasses import dataclass
from html import escape
from pathlib import Path
from string import Template
from typing import Any, TypedDict, cast

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import greeble.demo as demo
from greeble.demo import (
    load_component_stylesheets,
    load_component_template,
)

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8045))

ROOT = Path(__file__).resolve().parents[2]
CPTS = ROOT / "packages" / "greeble_components" / "components"
CORE_ASSETS = ROOT / "packages" / "greeble_core" / "assets" / "css"


# Re-export selected helpers so tests can import them from this module
def account_slug(account: Account) -> str:  # noqa: D401 - delegate
    return demo.account_slug(account)


def account_status_display(account: Account) -> tuple[str, str]:  # noqa: D401 - delegate
    return demo.account_status_display(account)


def sort_accounts(accounts: Iterable[Any], field: str, direction: str) -> list[Any]:  # noqa: D401 - delegate
    return cast(list[Any], demo.sort_accounts(accounts, field, direction))


def render_account_rows(accounts: Iterable[Any]) -> str:  # noqa: D401 - delegate
    return demo.render_account_rows(accounts)


def toast_fragment(level: str, title: str, message: str, *, icon: str | None = None) -> str:  # noqa: D401 - delegate
    return demo.toast_fragment(level, title, message, icon=icon)


def render_signin_group(email: str, error: str | None, *, swap_oob: bool) -> str:  # noqa: D401 - delegate
    return demo.render_signin_group(email, error, swap_oob=swap_oob)


def render_valid_email_group(email: str, *, swap_oob: bool) -> str:  # noqa: D401 - delegate
    return demo.render_valid_email_group(email, swap_oob=swap_oob)


def validate_signin_email(email: str) -> str | None:  # noqa: D401 - delegate
    return demo.validate_signin_email(email)


def render_feed_items(
    messages: Iterable[str], counter: Iterator[int], *, batch_size: int = 3
) -> str:  # noqa: D401 - delegate
    return demo.render_feed_items(messages, cast(Iterator[int], counter), batch_size=batch_size)


MODAL_PARTIAL = load_component_template(CPTS, "modal", "modal.partial.html")
DRAWER_TRIGGER = load_component_template(CPTS, "drawer", "drawer.html")
DRAWER_PARTIAL = load_component_template(CPTS, "drawer", "drawer.partial.html")
PALETTE_TEMPLATE = load_component_template(CPTS, "palette", "palette.html")
TABS_TEMPLATE = load_component_template(CPTS, "tabs", "tabs.html")
INFINITE_LIST_TEMPLATE = load_component_template(CPTS, "infinite-list", "infinite-list.html")
DROPDOWN_TEMPLATE = load_component_template(CPTS, "dropdown", "dropdown.html")
STEPPER_TEMPLATE = load_component_template(CPTS, "stepper", "stepper.html")
FORM_TEMPLATE = load_component_template(CPTS, "form-validated", "form.html")
FORM_INVALID_PARTIAL = load_component_template(CPTS, "form-validated", "form.partial.html")
AUDIO_RECORDER_TEMPLATE = load_component_template(CPTS, "audio-recorder", "audio-recorder.html")
DRAGGABLE_CARD_TEMPLATE = load_component_template(CPTS, "draggable-card", "draggable-card.html")
DROP_CANVAS_TEMPLATE = load_component_template(CPTS, "drop-canvas", "drop-canvas.html")
DROP_ZONE_TEMPLATE = load_component_template(CPTS, "drop-zone", "drop-zone.html")
FILE_UPLOAD_TEMPLATE = load_component_template(CPTS, "file-upload", "file-upload.html")
STEP_PROGRESS_TEMPLATE = load_component_template(CPTS, "step-progress", "step-progress.html")
SWAP_SELECT_TEMPLATE = load_component_template(CPTS, "swap-select", "swap-select.html")
TYPE_BADGE_TEMPLATE = load_component_template(CPTS, "type-badge", "type-badge.html")
NAV_TEMPLATE = load_component_template(CPTS, "nav", "nav.html")
SIDEBAR_TEMPLATE = load_component_template(CPTS, "sidebar", "sidebar.html")
FOOTER_TEMPLATE = load_component_template(CPTS, "footer", "footer.html")
MOBILE_MENU_TEMPLATE = load_component_template(CPTS, "mobile-menu", "mobile-menu.html")

COMPONENT_CSS = load_component_stylesheets(
    CPTS,
    (
        ("button", "button.css"),
        ("input", "input.css"),
        ("modal", "modal.css"),
        ("toast", "toast.css"),
        ("table", "table.css"),
        ("drawer", "drawer.css"),
        ("dropdown", "dropdown.css"),
        ("palette", "palette.css"),
        ("stepper", "stepper.css"),
        ("infinite-list", "infinite-list.css"),
        ("form-validated", "form.css"),
        ("tabs", "tabs.css"),
        ("audio-recorder", "audio-recorder.css"),
        ("draggable-card", "draggable-card.css"),
        ("drop-canvas", "drop-canvas.css"),
        ("drop-zone", "drop-zone.css"),
        ("file-upload", "file-upload.css"),
        ("step-progress", "step-progress.css"),
        ("swap-select", "swap-select.css"),
        ("type-badge", "type-badge.css"),
        ("nav", "nav.css"),
        ("sidebar", "sidebar.css"),
        ("footer", "footer.css"),
        ("mobile-menu", "mobile-menu.css"),
    ),
)

SITE_STATIC = Path(__file__).parent / "static"

app = FastAPI(title="Greeble Landing Demo")
app.mount(
    "/static/greeble",
    StaticFiles(directory=str(CORE_ASSETS)),
    name="greeble-static",
)
app.mount(
    "/static/images",
    StaticFiles(directory=str(ROOT / "public" / "images")),
    name="example-images",
)
# Serve site-specific assets (favicon, icons)
app.mount(
    "/static",
    StaticFiles(directory=str(SITE_STATIC)),
    name="site-static",
)


@dataclass
class Product:
    sku: str
    name: str
    tagline: str
    price: float
    inventory: int
    category: str
    description: str


@dataclass
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
FEED_MESSAGES = (
    "Automation queued background job.",
    "Webhook delivered to analytics partner.",
    "Status page updated for customers.",
)


class TabContent(TypedDict):
    title: str
    description: str
    items: list[str]


class StepContent(TypedDict):
    title: str
    description: str
    tasks: list[str]
    prev: str | None
    next: str | None


_TAB_CONTENT: dict[str, TabContent] = {
    "overview": {
        "title": "Mission control",
        "description": "Consolidate launches, async updates, and approvals in one workspace.",
        "items": [
            "Track blockers and owners in real time.",
            "Broadcast launch status to every stakeholder.",
            "Pipe alerts to Slack, Teams, and email.",
        ],
    },
    "pricing": {
        "title": "Usage-based pricing",
        "description": "Volume discounts unlock after 50 seats with custom invoicing support.",
        "items": [
            "$24/month starter tier with 10 seats included.",
            "Scale tier adds workflow automation and advanced analytics.",
            "Enterprise tier includes SSO, audit logs, and 24/7 support.",
        ],
    },
    "integrations": {
        "title": "Integrations",
        "description": "Connect your launch tooling ecosystem in a few clicks.",
        "items": [
            "Slack & Teams updates for status announcements.",
            "Linear issue syncing for launch blockers.",
            "Segment and RudderStack event streaming.",
        ],
    },
}


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
    <link rel="stylesheet" href="/static/greeble/greeble-landing.css" />
    <link rel="icon" href="/static/favicon.ico" sizes="any" />
    <link rel="icon" href="/static/greeble-icon-black.svg" type="image/svg+xml" media="(prefers-color-scheme: light)" />
    <link rel="icon" href="/static/greeble-icon-white.svg" type="image/svg+xml" media="(prefers-color-scheme: dark)" />
    <style>
      :root {
        color-scheme: light dark;
      }
      body { margin: 0; }
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
        /* 1/6 | 2/3 | 1/6 column layout */
        grid-template-columns: 1fr 4fr 1fr;
      }
      /* Center all sections into the middle column */
      main.landing > * { grid-column: 2; }
      /* Responsive adjustments */
      @media (max-width: 768px) {
        main.landing {
          grid-template-columns: 1fr;
          padding: clamp(1rem, 4vw, 2rem);
        }
        main.landing > * { grid-column: 1; }
        header.site-header {
          padding: 1rem clamp(1rem, 4vw, 2rem);
          flex-direction: column;
          align-items: flex-start;
          gap: .75rem;
        }
      }
      section.demo {
        display: grid;
        gap: 1.25rem;
        padding: 1.5rem;
        border-radius: 0.7rem;
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
        border-radius: .5rem;
        padding: 1rem;
      }
      .demo-listbox {
        list-style: none;
        padding: 0;
        margin: 0;
        max-height: 14rem;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: .5rem;
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
      /* Increase padding for early-access input */
      #request-access-form .greeble-input {
        padding: .9rem 1rem;
      }
      .feed-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
      }
      /* Demo group styling */
      .demo-group {
        display: grid;
        gap: 1.5rem;
        padding: 2rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      .demo-group:last-child {
        border-bottom: none;
      }
      .demo-group__header {
        display: grid;
        gap: 0.5rem;
        padding-bottom: 1rem;
      }
      .demo-group__header h2 {
        margin: 0;
        background: linear-gradient(135deg, #93c5fd 0%, #c4b5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      .demo-group__description {
        margin: 0;
        color: rgba(255, 255, 255, 0.65);
        font-size: 1.05rem;
      }
      /* App layout with sidebar */
      .app-layout {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
      }
      .app-layout__body {
        display: flex;
        flex: 1;
      }
      .app-layout__content {
        flex: 1;
        min-width: 0;
        overflow-x: hidden;
      }
      /* Adjust main for sidebar layout */
      main.landing {
        padding: clamp(1.5rem, 3vw, 3rem);
        display: grid;
        gap: 2.5rem;
        max-width: 64rem;
        margin: 0 auto;
      }
      /* Mobile menu root */
      #mobile-menu-root {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 200;
      }
      #mobile-menu-root > * {
        pointer-events: auto;
      }
      /* Hide sidebar on mobile */
      @media (max-width: 1024px) {
        .greeble-sidebar { display: none; }
      }
$component_css
    </style>
    <script src="https://unpkg.com/htmx.org@1.9.12" defer></script>
    <script src="https://unpkg.com/htmx.org/dist/ext/sse.js" defer></script>
  </head>
  <body>
    <div class="app-layout">
      <div id="greeble-toasts" aria-live="polite" aria-atomic="false"></div>
      <div id="modal-root" hx-target="this"></div>
      <div id="drawer-root" hx-target="this"></div>
      <div id="mobile-menu-root"></div>
      $nav
      <div class="app-layout__body">
        $sidebar
        <div class="app-layout__content">
          <main class="landing">
            $body
          </main>
        </div>
      </div>
      $footer
    </div>
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
    return HTMLResponse(
        layout.substitute(
            body=body_html,
            component_css=COMPONENT_CSS,
            nav=NAV_TEMPLATE,
            sidebar=SIDEBAR_TEMPLATE,
            footer=FOOTER_TEMPLATE,
        )
    )


def build_sign_in_section() -> str:
    initial_group = render_signin_group("", None, swap_oob=False)
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


def build_dropdown_section() -> str:
    return f"""
<section class="demo" id="workspace-actions">
  <header>
    <h2 class="greeble-heading-2">Workspace actions</h2>
    <p>Trigger HTMX-powered commands directly from a dropdown menu.</p>
  </header>
  {DROPDOWN_TEMPLATE}
  <div id="workspace-panel" class="greeble-card" aria-live="polite"></div>
  <div id="invite-root" aria-live="polite"></div>
</section>
    """


def build_palette_section() -> str:
    return f"""
<section class="demo" id="command-palette-demo">
  {PALETTE_TEMPLATE}
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
    return f"""
<section class="demo" id="product-tabs-section">
  {TABS_TEMPLATE}
</section>
    """


def build_drawer_section() -> str:
    return f"""
<section class="demo" id="promotions">
  <header>
    <h2 class="greeble-heading-2">Promotions Drawer</h2>
    <p>Open the drawer to explore upgrade perks and request a walkthrough.</p>
  </header>
  {DRAWER_TRIGGER}
</section>
    """


def build_infinite_list_section() -> str:
    return f"""
<section class="demo" id="infinite-updates">
  {INFINITE_LIST_TEMPLATE}
</section>
    """


def build_stepper_section() -> str:
    return f"""
<section class="demo" id="launch-stepper">
  {STEPPER_TEMPLATE}
</section>
    """


def build_validated_form_section() -> str:
    return f"""
<section class="demo" id="request-access-form">
  {FORM_TEMPLATE}
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


# --- New Component Section Builders ---


def build_audio_recorder_section() -> str:
    return f"""
<section class="demo" id="audio-recorder-demo">
  <header>
    <h2 class="greeble-heading-2">Audio Recorder</h2>
    <p>Record audio clips with MediaRecorder API and submit via HTMX.</p>
  </header>
  {AUDIO_RECORDER_TEMPLATE}
</section>
    """


def build_file_upload_section() -> str:
    return f"""
<section class="demo" id="file-upload-demo">
  <header>
    <h2 class="greeble-heading-2">File Upload</h2>
    <p>Multi-mode file input with tabs for file, URL, and paste.</p>
  </header>
  {FILE_UPLOAD_TEMPLATE}
</section>
    """


def build_drop_zone_section() -> str:
    return f"""
<section class="demo" id="drop-zone-demo">
  <header>
    <h2 class="greeble-heading-2">Drop Zone</h2>
    <p>Drag-and-drop file upload area with HTMX integration.</p>
  </header>
  {DROP_ZONE_TEMPLATE}
</section>
    """


def build_swap_select_section() -> str:
    return f"""
<section class="demo" id="swap-select-demo">
  <header>
    <h2 class="greeble-heading-2">Swap Select</h2>
    <p>Paired dropdowns with a swap button for source/target selection.</p>
  </header>
  {SWAP_SELECT_TEMPLATE}
</section>
    """


def build_type_badge_section() -> str:
    return f"""
<section class="demo" id="type-badge-demo">
  <header>
    <h2 class="greeble-heading-2">Type Badges</h2>
    <p>Colored badges for indicating content and data types in pipelines.</p>
  </header>
  <div class="cluster">
    {TYPE_BADGE_TEMPLATE}
  </div>
</section>
    """


def build_step_progress_section() -> str:
    return f"""
<section class="demo" id="step-progress-demo">
  <header>
    <h2 class="greeble-heading-2">Step Progress</h2>
    <p>Progress indicator for multi-step workflows with timing info.</p>
  </header>
  {STEP_PROGRESS_TEMPLATE}
</section>
    """


def build_pipeline_builder_section() -> str:
    """Combined draggable cards + drop canvas for a pipeline builder demo."""
    return f"""
<section class="demo" id="pipeline-builder">
  <header>
    <h2 class="greeble-heading-2">Pipeline Builder</h2>
    <p>Drag cards from the palette onto the canvas to build a workflow.</p>
  </header>
  <div class="grid-two">
    <aside>
      <h3 class="greeble-heading-3">Components</h3>
      {DRAGGABLE_CARD_TEMPLATE}
    </aside>
    <article>
      {DROP_CANVAS_TEMPLATE}
    </article>
  </div>
</section>
    """


# --- Grouped Section Builders ---


def build_section_group(title: str, description: str, sections: list[str]) -> str:
    """Wrap multiple demo sections in a labeled group."""
    inner = "\n".join(sections)
    return f"""
<div class="demo-group" id="{title.lower().replace(" ", "-")}-group">
  <header class="demo-group__header">
    <h2 class="greeble-heading-1">{title}</h2>
    <p class="demo-group__description">{description}</p>
  </header>
  {inner}
</div>
    """


@app.get("/", response_class=HTMLResponse)
async def landing() -> HTMLResponse:
    # Group 1: Authentication & Forms
    auth_forms = build_section_group(
        "Authentication & Forms",
        "Sign-in flows, validated inputs, and form handling patterns.",
        [build_sign_in_section(), build_validated_form_section()],
    )

    # Group 2: Navigation & Selection
    navigation = build_section_group(
        "Navigation & Selection",
        "Tabs, dropdowns, command palettes, and swap selects for user choices.",
        [
            build_tabs_section(),
            build_dropdown_section(),
            build_palette_section(),
            build_swap_select_section(),
        ],
    )

    # Group 3: Data Display
    data_display = build_section_group(
        "Data Display",
        "Tables, badges, and infinite lists for presenting information.",
        [build_table_section(), build_type_badge_section(), build_infinite_list_section()],
    )

    # Group 4: Overlays & Dialogs
    overlays = build_section_group(
        "Overlays & Dialogs",
        "Modals, drawers, and toasts for contextual interactions.",
        [build_drawer_section()],
    )

    # Group 5: File & Media
    file_media = build_section_group(
        "File & Media",
        "Upload files, record audio, and handle media inputs.",
        [build_file_upload_section(), build_drop_zone_section(), build_audio_recorder_section()],
    )

    # Group 6: Workflow & Pipelines
    workflows = build_section_group(
        "Workflow & Pipelines",
        "Steppers, progress indicators, and drag-and-drop pipeline builders.",
        [build_stepper_section(), build_step_progress_section(), build_pipeline_builder_section()],
    )

    # Group 7: Live Updates
    live = build_section_group(
        "Live Updates",
        "Server-Sent Events for real-time status and notifications.",
        [build_sse_section()],
    )

    sections = "\n".join(
        [auth_forms, navigation, data_display, overlays, file_media, workflows, live]
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
        toast_html = toast_fragment(
            "danger",
            "Check email",
            "Enter a valid email to continue.",
        )
        toast = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
        return HTMLResponse(MODAL_PARTIAL + toast, status_code=400)

    toast_html = toast_fragment(
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
    toast_html = toast_fragment("info", "Subscribed", "You're on the launch list.")
    html = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    return HTMLResponse(html)


@app.get("/workspace/settings", response_class=HTMLResponse)
async def workspace_settings() -> HTMLResponse:
    html = """
<div id="workspace-panel" class="greeble-card">
  Settings panel loaded. Adjust billing and integrations here.
</div>
    """
    return HTMLResponse(html)


@app.post("/workspace/invite", response_class=HTMLResponse)
async def workspace_invite(email: str = Form("")) -> HTMLResponse:
    toast = toast_fragment("success", "Invite queued", "We'll email your teammate a magic link.")
    body = (
        '<div id="invite-root">Invite request received.</div>'
        + f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
    )
    headers = {"HX-Trigger": json.dumps({"greeble:menu:select": {"action": "invite"}})}
    return HTMLResponse(body, headers=headers)


@app.post("/palette/search", response_class=HTMLResponse)
async def palette_search(q: str = Form("")) -> HTMLResponse:
    query = q.strip()
    matches = demo.filter_products(PRODUCTS, query) if query else list(PRODUCTS[:4])
    html = demo.render_palette_results(matches)
    headers = {"HX-Trigger": json.dumps({"greeble:palette:results": {"count": len(matches)}})}
    return HTMLResponse(html, headers=headers)


@app.post("/palette/select", response_class=HTMLResponse)
async def palette_select(sku: str = Form(...)) -> HTMLResponse:
    product = _PRODUCTS_BY_SKU.get(sku)
    if not product:
        raise HTTPException(status_code=404, detail="Unknown product")
    detail_html = demo.render_palette_detail(product)
    headers = {"HX-Trigger": json.dumps({"greeble:palette:select": {"sku": sku}})}
    return HTMLResponse(detail_html, headers=headers)


def _query_accounts(page: int, field: str, direction: str, page_size: int = 3) -> list[Account]:
    sorted_accounts = sort_accounts(ACCOUNTS, field, direction)
    start = (page - 1) * page_size
    end = start + page_size
    return sorted_accounts[start:end]


def _get_account_by_slug(slug: str) -> Account:
    try:
        return cast(Account, demo.find_account_by_slug(ACCOUNTS, slug))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Unknown account") from exc


_STEPPER_STEPS: dict[str, StepContent] = {
    "plan": {
        "title": "Plan launch",
        "description": "Confirm timeline, owners, and announcement strategy.",
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
        "description": "Share launch briefs, escalation paths, and FAQ updates.",
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
        "description": "Monitor rollout, communicate status, and capture feedback.",
        "tasks": [
            "Monitor health metrics and alert thresholds.",
            "Post launch status to customers and partners.",
            "Collect feedback for the retro.",
        ],
        "prev": "enable",
        "next": None,
    },
}


def render_stepper_content(step_key: str) -> str:
    data = _STEPPER_STEPS.get(step_key)
    if not data:
        raise HTTPException(status_code=404, detail="Unknown step")
    tasks_html = "\n".join(f"    <li>{escape(task)}</li>" for task in data["tasks"])
    actions: list[str] = []
    if prev_key := data["prev"]:
        actions.append(_stepper_button(prev_key, "Back", primary=False))
    if next_key := data["next"]:
        actions.append(_stepper_button(next_key, "Continue", primary=True))
    actions_html = "\n".join(actions)
    return (
        '<section class="greeble-stepper__content" data-step="{key}">\n'
        '  <h3 class="greeble-heading-3">{title}</h3>\n'
        "  <p>{description}</p>\n"
        '  <ul class="greeble-stepper__tasks">\n{tasks}\n  </ul>\n'
        '  <div class="greeble-stepper__actions">\n{actions}\n  </div>\n'
        "</section>\n"
    ).format(
        key=escape(step_key),
        title=escape(data["title"]),
        description=escape(data["description"]),
        tasks=tasks_html,
        actions=actions_html,
    )


def _stepper_button(target: str, label: str, *, primary: bool) -> str:
    variant = " greeble-button--primary" if primary else ""
    escaped_target = escape(target)
    return (
        f'<button class="greeble-button{variant}" type="button"\n'
        f'        hx-get="/stepper/{escaped_target}"\n'
        f'        hx-target="#stepper-panel"\n'
        f'        hx-swap="innerHTML">\n  {label}\n</button>'
    )


@app.get("/table", response_class=HTMLResponse)
async def table_rows(request: Request) -> HTMLResponse:
    params = request.query_params
    page = int(params.get("page", 1))
    sort_param = params.get("sort", "org:asc")
    field, _, direction = sort_param.partition(":")
    direction = direction or "asc"
    rows_html = demo.table_rows(
        ACCOUNTS,
        page=page,
        field=field or "org",
        direction=direction,
    )

    if not rows_html:
        return HTMLResponse('<tr><td colspan="5">No matching accounts.</td></tr>')

    payload = json.dumps({"greeble:table:update": {"page": page, "sort": f"{field}:{direction}"}})
    headers = {"HX-Trigger": payload}
    return HTMLResponse(rows_html, headers=headers)


@app.post("/table/search", response_class=HTMLResponse)
async def table_search(q: str = Form("")) -> HTMLResponse:
    query = q.strip()
    if not query:
        html = demo.table_rows(ACCOUNTS, page=1, field="org", direction="asc")
        headers = {"HX-Trigger": json.dumps({"greeble:table:update": {"query": ""}})}
        return HTMLResponse(html, headers=headers)

    matches = demo.filter_accounts(ACCOUNTS, query)
    if not matches:
        return HTMLResponse('<tr><td colspan="5">No accounts match this search.</td></tr>')

    headers = {
        "HX-Trigger": json.dumps(
            {"greeble:table:update": {"query": query, "results": len(matches)}}
        )
    }
    return HTMLResponse(demo.render_account_rows(matches), headers=headers)


@app.post("/table/export", response_class=HTMLResponse)
async def table_export() -> HTMLResponse:
    toast_html = toast_fragment(
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
    toast_html = toast_fragment(
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
    toast_html = toast_fragment(
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
    toast_html = toast_fragment(
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
    toast_html = toast_fragment(
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
    data = _TAB_CONTENT.get(tab_key)
    if not data:
        raise HTTPException(status_code=404, detail="Unknown tab")

    items_html = "\n".join(f"    <li>{escape(item)}</li>" for item in data["items"])
    html = Template(
        """
<section class="greeble-tabs__content" data-tab="$key">
  <h3 class="greeble-heading-3">$title</h3>
  <p>$description</p>
  <ul class="greeble-tabs__list">
$items
  </ul>
</section>
        """
    ).substitute(
        key=escape(tab_key),
        title=escape(data["title"]),
        description=escape(data["description"]),
        items=items_html,
    )
    headers = {
        "HX-Trigger": json.dumps({"greeble:tab:change": {"tab": tab_key}}),
    }
    return HTMLResponse(html, headers=headers)


@app.get("/drawer/open", response_class=HTMLResponse)
async def drawer_open() -> HTMLResponse:
    return HTMLResponse(DRAWER_PARTIAL)


@app.get("/drawer/close", response_class=HTMLResponse)
async def drawer_close() -> HTMLResponse:
    return HTMLResponse("")


@app.post("/drawer/subscribe", response_class=HTMLResponse)
async def drawer_subscribe(email: str = Form("")) -> HTMLResponse:
    value = email.strip()
    if not value or "@" not in value:
        toast = toast_fragment(
            "danger",
            "Try again",
            "Enter a valid work email to receive updates.",
        )
        body = f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
        return HTMLResponse(body, status_code=400)

    toast = toast_fragment(
        "success",
        "Walkthrough requested",
        f"We'll contact {escape(value)} shortly.",
    )
    body = (
        '<div id="drawer-root" hx-swap-oob="true"></div>'
        f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
    )
    headers = {
        "HX-Trigger": json.dumps({"greeble:drawer:close": True}),
    }
    return HTMLResponse(body, headers=headers)


@app.get("/stepper/{step_key}", response_class=HTMLResponse)
async def stepper_step(step_key: str) -> HTMLResponse:
    html = render_stepper_content(step_key)
    headers = {
        "HX-Trigger": json.dumps({"greeble:stepper:change": {"step": step_key}}),
    }
    return HTMLResponse(html, headers=headers)


@app.post("/auth/validate", response_class=HTMLResponse)
async def auth_validate(email: str = Form("")) -> HTMLResponse:
    error = validate_signin_email(email)
    html = render_signin_group(email, error, swap_oob=False)
    status = 400 if error else 200
    return HTMLResponse(html, status_code=status)


@app.post("/auth/sign-in", response_class=HTMLResponse)
async def auth_sign_in(email: str = Form("")) -> HTMLResponse:
    if error := validate_signin_email(email):
        group_html = render_signin_group(email, error, swap_oob=True)
        status_area = '<div id="sign-in-status">Fix the highlighted field to continue.</div>'
        return HTMLResponse(group_html + status_area, status_code=400)

    reset_group = render_signin_group("", None, swap_oob=True)
    toast_html = toast_fragment(
        "success",
        "Signed in",
        f"Signed in as {email.strip()}.",
    )
    toast_html = f'<div id="greeble-toasts" hx-swap-oob="true">{toast_html}</div>'
    status_area = '<div id="sign-in-status">We sent a magic link to your inbox.</div>'
    return HTMLResponse(reset_group + toast_html + status_area)


@app.post("/form/validate", response_class=HTMLResponse)
async def validated_form_check(email: str = Form("")) -> HTMLResponse:
    if validate_signin_email(email):
        return HTMLResponse(FORM_INVALID_PARTIAL, status_code=400)
    return HTMLResponse(render_valid_email_group(email, swap_oob=False))


@app.post("/form/submit", response_class=HTMLResponse)
async def validated_form_submit(email: str = Form("")) -> HTMLResponse:
    if validate_signin_email(email):
        return HTMLResponse(FORM_INVALID_PARTIAL, status_code=400)

    reset_group = render_valid_email_group("", swap_oob=True)
    toast = toast_fragment(
        "success",
        "Request received",
        "We will reach out with onboarding steps shortly.",
    )
    body = (
        f"{reset_group}"
        f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
        '<div id="form-status">Thanks! We\'ll reach out with next steps.</div>'
    )
    headers = {"HX-Trigger": json.dumps({"greeble:form:submitted": True})}
    return HTMLResponse(body, headers=headers)


@app.get("/list", response_class=HTMLResponse)
async def infinite_list() -> HTMLResponse:
    return HTMLResponse(render_feed_items(FEED_MESSAGES, _FEED_COUNTER, batch_size=3))


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


# --- New Component Endpoints ---


# Swap Select options
SWAP_OPTIONS = {
    "languages": [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("de", "German"),
        ("ja", "Japanese"),
        ("zh", "Chinese"),
    ],
}


@app.get("/options/source", response_class=HTMLResponse)
@app.get("/options/target", response_class=HTMLResponse)
async def swap_select_options() -> HTMLResponse:
    options = "\n".join(
        f'<option value="{code}">{name}</option>' for code, name in SWAP_OPTIONS["languages"]
    )
    return HTMLResponse(options)


@app.post("/audio/upload", response_class=HTMLResponse)
async def audio_upload() -> HTMLResponse:
    toast = toast_fragment("success", "Audio received", "Your recording has been uploaded.")
    body = (
        '<div id="audio-recorder-result">Audio uploaded successfully!</div>'
        f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
    )
    return HTMLResponse(body)


@app.post("/files/upload", response_class=HTMLResponse)
async def files_upload() -> HTMLResponse:
    toast = toast_fragment("success", "Files uploaded", "Your files have been processed.")
    body = (
        '<div id="drop-zone-result">Files uploaded successfully!</div>'
        f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
    )
    return HTMLResponse(body)


@app.post("/pipeline/run", response_class=HTMLResponse)
async def pipeline_run() -> HTMLResponse:
    toast = toast_fragment("info", "Pipeline started", "Processing your workflow...")
    body = (
        '<div id="drop-canvas-output" class="greeble-card">Pipeline executed! Results would appear here.</div>'
        f'<div id="greeble-toasts" hx-swap-oob="true">{toast}</div>'
    )
    headers = {"HX-Trigger": json.dumps({"greeble:pipeline:complete": True})}
    return HTMLResponse(body, headers=headers)


# Mobile menu endpoints
@app.get("/menu/open", response_class=HTMLResponse)
async def menu_open() -> HTMLResponse:
    return HTMLResponse(MOBILE_MENU_TEMPLATE)


@app.get("/menu/close", response_class=HTMLResponse)
async def menu_close() -> HTMLResponse:
    return HTMLResponse("")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("examples.site.landing:app", host=str(HOST), port=int(PORT), reload=True)
