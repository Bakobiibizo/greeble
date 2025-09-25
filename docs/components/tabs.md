# Tabs

- Purpose: Present multiple views (overview, pricing, integrations) within a single layout.
- Structure: Buttons in the tablist fetch content for `#tab-panel` using HTMX. Update
  `aria-selected` and optional `data-tab` attributes as swaps occur.
- Endpoint: `GET /tabs/{tabKey}` returns a fragment for the requested tab.
- Events: `HX-Trigger: {"greeble:tab:change": {"tab": "integrations"}}` after rendering each
  panel.
- Accessibility: Uses `role="tablist"`, `role="tab"`, and `role="tabpanel"`. The panel is
  `aria-live="polite"` so screen readers hear the new content.
- Theming hooks: `.greeble-tabs__tab`, `.greeble-tabs__tab[aria-selected="true"]`, and
  `.greeble-tabs__panel`.

## Include in template

```jinja
{% include "greeble/tabs.html" %}
```

## Copy & Paste

```html
<section class="greeble-tabs-shell" aria-labelledby="product-tabs-heading">
  <header class="greeble-tabs-shell__header">
    <h2 id="product-tabs-heading" class="greeble-heading-2">Product overview</h2>
    <p>Explore overview, pricing, and integrations without leaving the page.</p>
  </header>
  <div class="greeble-tabs" role="tablist" aria-label="Product content">
    <button role="tab" data-tab="overview" aria-selected="true" aria-controls="tab-panel"
            class="greeble-tabs__tab" hx-get="/tabs/overview" hx-target="#tab-panel" hx-swap="innerHTML">
      <span class="greeble-tabs__label">Overview</span>
    </button>
    <button role="tab" data-tab="pricing" aria-selected="false" aria-controls="tab-panel"
            class="greeble-tabs__tab" hx-get="/tabs/pricing" hx-target="#tab-panel" hx-swap="innerHTML">
      <span class="greeble-tabs__label">Pricing</span>
    </button>
    <button role="tab" data-tab="integrations" aria-selected="false" aria-controls="tab-panel"
            class="greeble-tabs__tab" hx-get="/tabs/integrations" hx-target="#tab-panel" hx-swap="innerHTML">
      <span class="greeble-tabs__label">Integrations</span>
    </button>
  </div>
  <div id="tab-panel" class="greeble-tabs__panel" role="tabpanel" aria-live="polite"
       hx-get="/tabs/overview" hx-trigger="load" hx-target="this" hx-swap="innerHTML">
    <p>Loading tab…</p>
  </div>
</section>
```

Panel response example:

```html
<section class="greeble-tabs__content" data-tab="overview">
  <h3 class="greeble-heading-3">Mission control</h3>
  <p>Consolidate launches, async updates, and approvals in a single workspace.</p>
  <ul class="greeble-tabs__list">
    <li>Track blockers and owners in real time.</li>
    <li>Broadcast launch status to every stakeholder.</li>
    <li>Pipe alerts to Slack, Teams, and email.</li>
  </ul>
</section>
```

## Keyboard map

- Arrow Left/Right – Move focus between tabs in the tablist.
- Home/End – Jump to the first/last tab.
- Enter/Space – Activate the focused tab (fetch panel content).
- Tab / Shift+Tab – Move between the tablist and the panel content.

## Response matrix

- GET /tabs/{tabKey}
  - 200 OK — returns panel fragment for the requested tab
  - Headers: `HX-Trigger: {"greeble:tab:change": {"tab": "<tabKey>"}}`

## View source

- Template: [tabs.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/tabs/templates/tabs.html)
- Partial: [tabs.partial.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/tabs/templates/tabs.partial.html)
- Styles: [tabs.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/tabs/static/tabs.css)
