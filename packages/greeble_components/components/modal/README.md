# Modal Component (Placeholder)

- **Purpose:** Dialog with focus trap, backdrop, and close controls.
- **Inputs:** Trigger markup via hx-get to open; form inputs within modal.
- **Outputs:** Server partials: open, close (empty), submit result.
- **Dependencies:** HTMX, optional Hyperscript; `greeble_core` tokens.
- **Endpoints:** GET /modal/example, GET /modal/close, POST /modal/submit
- **Events:** `greeble:modal:open`, `greeble:modal:close`
- **Accessibility:** role=dialog, aria-modal=true, managed focus.
