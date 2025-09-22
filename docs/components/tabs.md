# Tabs

- Purpose: Tablist with per-tab content.
- Inputs: Tab key via hx-get.
- Endpoints: GET /tabs/{tabKey}
- Events: `greeble:tab:change`.
- Accessibility: role=tablist/role=tab; aria-controls/selected.
- States: Active/inactive; loading content.
- Theming hooks: Tab styles; panel spacing.

## Copy & Paste Usage

Markup:

```html
<div class="greeble-tabs" role="tablist">
  <button role="tab" aria-selected="true" aria-controls="tab-panel" hx-get="/tabs/one" hx-target="#tab-panel" hx-swap="innerHTML">One</button>
  <button role="tab" aria-selected="false" aria-controls="tab-panel" hx-get="/tabs/two" hx-target="#tab-panel" hx-swap="innerHTML">Two</button>
</div>
<div id="tab-panel" role="tabpanel" hx-get="/tabs/one" hx-trigger="load" hx-swap="innerHTML"></div>
```

Server returns a fragment like `<section>Content for {tabKey}</section>`. You may emit `HX-Trigger` headers (e.g., `{"greeble:tab:change": {"key": "one"}}`).
