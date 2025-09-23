# Toasts
- **Purpose:** Global notification queue populated via HTMX out-of-band swaps.
- **Inputs:** Servers return `<div id="greeble-toasts" hx-swap-oob="true">…</div>` fragments with `.greeble-toast` items.
- **Outputs:** Root region markup plus toast item snippet with dismiss controls.
- **Dependencies:** HTMX for swaps; `greeble_core` tokens; component CSS provides variant colors.
- **Events:** Suggested event payload `{"greeble:toast": {"level": "success"}}` for analytics or telemetry.
- **Accessibility:** Root `role="region"` + `aria-live="polite"`; each toast `role="status"`; dismiss buttons labeled.
