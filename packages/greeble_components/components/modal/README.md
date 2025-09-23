# Modal Component

- **Purpose:** Server-rendered dialog with focus management, custom badge, and action footer.
- **Inputs:** Trigger button (`hx-get="/modal/example"`); form fields posted to `/modal/submit`.
- **Outputs:** Modal partial, empty close fragment, submit response (often includes toasts + HX-Trigger events).
- **Dependencies:** HTMX; optional Hyperscript script focuses `.greeble-modal__panel`; shares `greeble_core` tokens.
- **Endpoints:** `GET /modal/example`, `GET /modal/close`, `POST /modal/submit`.
- **Events:** Emit `greeble:modal:open` on load and `greeble:modal:close` after closing.
- **Accessibility:** `role="dialog"`, `aria-modal`, labelled header, close button with `aria-label`, panel `tabindex="-1"` for focus.
