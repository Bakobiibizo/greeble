# Tabs

- **Purpose:** Switch between related content panes using HTMX to fetch each panel.
- **Structure:** `tabs.html` renders the tablist and the `#tab-panel` container. Each button sets
  `hx-get` to load the relevant content.
- **Endpoints:** `GET /tabs/{tabKey}` returns markup for the requested panel.
- **Events:** Emit `HX-Trigger: {"greeble:tab:change": {"tab": "pricing"}}` when returning a panel
  if other UI should react to the selection.
- **Accessibility:** Buttons use `role="tab"` and `aria-selected`; the panel is `role="tabpanel"`
  with `aria-live="polite"` for announcements.
- **Theming:** Override `.greeble-tabs__tab[aria-selected="true"]` and `.greeble-tabs__panel` for
  brand-specific colours.
