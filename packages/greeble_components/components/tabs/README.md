# Tabs (Placeholder)
- **Purpose:** Tablist with per-tab content via hx-get.
- **Inputs:** Tab keys; hx-get endpoints.
- **Outputs:** Partial content per tab.
- **Dependencies:** HTMX; greeble_core.
- **Endpoints:** GET /tabs/{tabKey}
- **Events:** `greeble:tab:change`
- **Accessibility:** role=tablist/role=tab with aria-controls.
