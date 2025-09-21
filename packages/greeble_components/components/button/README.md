# Button Component (Placeholder)

- **Purpose:** Primary, secondary, icon, and split buttons.
- **Inputs:** HTML attributes (type, disabled), optional data attributes for variants.
- **Outputs:** No server output; acts as trigger for HTMX requests.
- **Dependencies:** `greeble_core` tokens; optional HTMX if used as trigger.
- **Events:** May emit `greeble:click` (optional, documented by consuming app).
- **Accessibility:** Visible focus; `aria-pressed` for toggle variants.
