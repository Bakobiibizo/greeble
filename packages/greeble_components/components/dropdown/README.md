# Dropdown Menu

- **Purpose:** Offer secondary actions without leaving the current view.
- **Trigger:** `<details class="greeble-dropdown">` relies on the native summary toggle so the menu
  works without JavaScript.
- **Menu items:** Buttons or anchors with `role="menuitem"`; add HTMX attributes to invoke server
  endpoints. Include keyboard hints or helper text with
  `.greeble-dropdown__item-kbd`/`.greeble-dropdown__item-hint`.
- **Events:** Use response headers (e.g., `HX-Trigger: {"greeble:menu:select": {"action": "invite"}}`)
  to notify the client when selections complete.
- **Accessibility:** `aria-haspopup="menu"` announces the summary button. The panel uses
  `role="menu"` and remains operable via keyboard. Focus states rely on the shared focus-ring token.
- **Theming:** Override `.greeble-dropdown__panel` and `.greeble-dropdown__item` for different menu
  shapes, shadows, or typography.
