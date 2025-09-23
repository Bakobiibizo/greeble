# Modal

- Purpose: Present blocking workflows (invite teammates, confirm actions) with server-rendered dialogs.
- Trigger: Button uses `hx-get="/modal/example"` to render into an empty `#modal-root` container.
- Endpoints: `GET /modal/example` returns the dialog; `GET /modal/close` clears the root; `POST /modal/submit` handles form submission and may emit HX-Trigger events or out-of-band toasts.
- Structure: Wrapper `.greeble-modal` with backdrop and focusable panel `.greeble-modal__panel`; header includes a close button; body hosts form content.
- Accessibility: `role="dialog"`, `aria-modal="true"`, labelled via `aria-labelledby`/`aria-describedby`; panel receives focus via `tabindex="-1"`; close button carries `aria-label`.
- Events: Emit `HX-Trigger: {"greeble:modal:open": true}` when returning the partial and `HX-Trigger-After-Swap` to signal closing.
- Theming hooks: Panel and actions inherit tokens; `.greeble-badge`, `.greeble-modal__actions`, `.greeble-checkbox` expose specific styling knobs.

## Server contract

- `GET /modal/example` returns the modal partial. Include `HX-Trigger: {"greeble:modal:open": true}`
  if other components need to know the modal opened.
- `GET /modal/close` should return an empty string. HTMX clears `#modal-root` immediately.
- `POST /modal/submit` handles the form. On success, return an empty modal root plus an out-of-band
  toast to close the dialog and inform the user. On validation failure, return the modal partial
  with inline errors and set the status to 400 so HTMX keeps the dialog mounted.

## Copy & Paste

```html
<button class="greeble-button greeble-button--primary" hx-get="/modal/example" hx-target="#modal-root" hx-swap="innerHTML">Invite teammates</button>
<div id="modal-root" aria-live="polite"></div>
```

Return the modal partial example to hydrate the dialog. Close endpoints should respond with an empty string to remove the modal from the DOM.

## Keyboard map

- Esc – Close the dialog (client should wire this to the close action when appropriate).
- Tab / Shift+Tab – Cycle focus within the dialog panel (focus trap).
- Enter – Activate focused button or submit the form when focus is inside a form control.

## Response matrix

- GET /modal/example
  - 200 OK — returns modal partial
  - Headers: optional `HX-Trigger: {"greeble:modal:open": true}`

- GET /modal/close
  - 200 OK — returns empty string to clear `#modal-root`

- POST /modal/submit
  - 200 OK (success) — returns:
    - Out-of-band updates: `#modal-root` cleared (empty element) and toast container with success toast
    - Headers: optional `HX-Trigger-After-Swap` to signal follow-up actions
  - 400 Bad Request (validation) — returns modal partial with inline errors; HTMX keeps dialog mounted
