<div class="landing-hero">
  <img src="../assets/images/logo-full.svg" alt="Greeble" class="landing-logo" width="280">
  <span class="docs-demo-badge">HTML-first components</span>
  <h1 class="text-gradient">Ship production UI without a SPA</h1>
  <p>Greeble pairs copy-and-paste components with HTMX helpers, design tokens, and framework adapters so you can build responsive dashboards in hours, not weeks.</p>
  <div class="landing-actions">
    <a class="greeble-button greeble-button--primary" href="/cli/">Install the CLI</a>
    <a class="greeble-button greeble-button--ghost" href="/components/">Browse components</a>
    <a class="greeble-button greeble-button--ghost" href="https://github.com/Bakobiibizo/greeble" rel="noopener" target="_blank">View source</a>
  </div>
</div>

<div class="landing-deck">

### Why teams pick Greeble

<div class="docs-demo-grid">
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Adaptive layouts</span>
      <h3>HTMX-first components</h3>
      <p>Each component ships a template, CSS, and server contract so partial rendering stays predictable.</p>
    </header>
    <div class="stack">
      <div class="cluster">
        <button class="greeble-button greeble-button--primary" type="button">Primary</button>
        <button class="greeble-button greeble-button--ghost" type="button">Ghost</button>
        <button class="greeble-button greeble-button--icon" type="button" aria-label="Dismiss">×</button>
      </div>
      <pre><code class="language-html">&lt;button class="greeble-button" hx-post="/actions" hx-target="#result"&gt;Save&lt;/button&gt;</code></pre>
    </div>
  </section>
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Framework adapters</span>
      <h3>FastAPI · Django · Flask</h3>
      <p>Drop-in helpers wire CSRF headers, toast middleware, and pagination utilities to HTMX responses.</p>
    </header>
    <ul class="docs-demo-list">
      <li><code>greeble.adapters.fastapi.template_response</code></li>
      <li><code>GreebleMessagesToToastsMiddleware</code> (Django)</li>
      <li><code>greeble.adapters.flask.template_response</code></li>
    </ul>
  </section>
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Design tokens</span>
      <h3>Tailwind &amp; CSS variables</h3>
      <p>Consume <code>greeble_core</code> tokens directly or bootstrap Tailwind with the bundled preset.</p>
    </header>
    <div class="stack">
      <pre><code class="language-js">module.exports = {
  presets: [require('./tools/greeble/tailwind/preset.cjs')],
  content: ['./templates/**/*.html']
};</code></pre>
      <pre><code class="language-css">.stack {
  display: grid;
  gap: var(--greeble-spacing-3);
}</code></pre>
    </div>
  </section>
</div>

### Live component samples

<div class="docs-demo-grid">
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Modal</span>
      <h3>Form inside modal</h3>
      <p>Progressive enhancement pattern with HTMX partial swaps and toast triggers.</p>
    </header>
    <div class="stack" id="docs-modal-demo">
      <button class="greeble-button" type="button" data-action="preview-modal">Preview modal pattern</button>
      <p class="docs-demo-note">Launches a modal in the FastAPI demo without interrupting this page.</p>
      <pre><code class="language-html">&lt;button class="greeble-button" hx-get="/demo/modal" hx-target="#modal-root" hx-swap="afterbegin"&gt;Invite teammate&lt;/button&gt;</code></pre>
    </div>
  </section>
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Table</span>
      <h3>Server-driven pagination</h3>
      <p>Pagination context pairs with adapters to produce consistent HX-Trigger payloads.</p>
    </header>
    <div class="stack">
      <table class="greeble-table">
        <thead>
          <tr>
            <th scope="col">Account</th>
            <th scope="col">Plan</th>
            <th scope="col">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Orbit Labs</td>
            <td>Scale</td>
            <td><span class="greeble-badge greeble-badge--success">Active</span></td>
          </tr>
          <tr>
            <td>Nova Civic</td>
            <td>Starter</td>
            <td><span class="greeble-badge greeble-badge--warning">Pending</span></td>
          </tr>
        </tbody>
      </table>
      <nav class="greeble-pagination" aria-label="Pagination">
        <button class="greeble-button" type="button" disabled>Prev</button>
        <span>Page 1 of 5</span>
        <button class="greeble-button" type="button">Next</button>
      </nav>
    </div>
  </section>
  <section class="docs-demo-card">
    <header>
      <span class="docs-demo-badge">Toasts</span>
      <h3>HX-Trigger notifications</h3>
      <p>Django/Flask middleware translate flash messages into toast payloads automatically.</p>
    </header>
    <div class="stack">
      <div id="docs-toast-demo" class="greeble-toast-region" aria-live="polite" aria-label="Notifications">
        <div class="greeble-toast greeble-toast--info">
          <div class="greeble-toast__body">
            <p class="greeble-toast__title">Panel loaded</p>
            <p class="greeble-toast__message">Triggered via HX-Trigger response header.</p>
          </div>
          <button class="greeble-icon-button greeble-toast__dismiss" type="button" aria-label="Dismiss">×</button>
        </div>
      </div>
      <pre><code class="language-python">return template_response(
    partial_template="panel.partial.html",
    triggers={"greeble:toast": {"level": "info", "message": "Panel loaded"}},
)</code></pre>
    </div>
  </section>
</div>

</div>

### Get started

- **Install** the CLI: `uv run pip install greeble`
- **Scaffold** a starter: `uv run greeble new apps/site --include-docs`
- **Wire** the Tailwind preset: `uv run greeble theme init`

### Keep exploring

- **Adapters** – Framework integrations and HTMX helpers [`/adapters/`](../adapters.md)
- **CLI** – Component scaffolding, starter workflow [`/cli/`](../cli.md)
- **Roadmap** – Track the Now / Next / Later milestones [`/roadmap/`](../roadmap.md)
- Overview
- Getting Started
- Components
- Patterns
- Accessibility

## Getting Started

Install Greeble using your preferred tool and include the core CSS and HTMX in your app shell.

```bash
uv add greeble
```

```bash
pip install greeble
```

```bash
poetry add greeble
```

Add assets in your HTML layout:

```html
<link rel="stylesheet" href="/static/greeble/greeble-core.css" />
<script src="https://unpkg.com/htmx.org@1.9.12" defer></script>
<script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
```

