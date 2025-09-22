# Drawer Component

- **Purpose:** Present contextual upgrades, filters, or settings in a right-aligned drawer.
- **Trigger:** `drawer.html` renders a primary button plus the empty `#drawer-root` container that
  receives drawer fragments via HTMX swaps.
- **Partial:** `drawer.partial.html` returns the dialog markup with backdrop, heading, feature list,
  and a follow-up form.
- **Endpoints:**
  - `GET /drawer/open` → returns the partial and may emit `HX-Trigger: {"greeble:drawer:open": true}`.
  - `GET /drawer/close` → returns an empty string to clear the root.
  - Optional POST (e.g., `/drawer/subscribe`) handles form submissions and can return out-of-band
    toasts.
- **Accessibility:** Uses `role="dialog"`, `aria-modal="true"`, and labelled headings. The panel
  receives focus (`tabindex="-1"`). Backdrop buttons include `aria-label` for screen readers.
- **Theming:** Customize `.greeble-drawer__panel`, `.greeble-drawer__eyebrow`, and
  `.greeble-drawer__actions` or override CSS variables for background/spacing.
