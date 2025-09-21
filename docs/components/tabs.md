# Tabs

- Purpose: Tablist with per-tab content.
- Inputs: Tab key via hx-get.
- Endpoints: GET /tabs/{tabKey}
- Events: `greeble:tab:change`.
- Accessibility: role=tablist/role=tab; aria-controls/selected.
- States: Active/inactive; loading content.
- Theming hooks: Tab styles; panel spacing.
