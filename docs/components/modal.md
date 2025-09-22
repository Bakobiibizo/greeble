# Modal

- Purpose: Present blocking workflows (invite teammates, confirm actions) with server-rendered dialogs.
- Trigger: Button uses `hx-get="/modal/example"` to render into an empty `#modal-root` container.
- Endpoints: `GET /modal/example` returns the dialog; `GET /modal/close` clears the root; `POST /modal/submit` handles form submission and may emit HX-Trigger events or out-of-band toasts.
- Structure: Wrapper `.greeble-modal` with backdrop and focusable panel `.greeble-modal__panel`; header includes a close button; body hosts form content.
- Accessibility: `role="dialog"`, `aria-modal="true"`, labelled via `aria-labelledby`/`aria-describedby`; panel receives focus via `tabindex="-1"`; close button carries `aria-label`.
- Events: Emit `HX-Trigger: {"greeble:modal:open": true}` when returning the partial and `HX-Trigger-After-Swap` to signal closing.
- Theming hooks: Panel and actions inherit tokens; `.greeble-badge`, `.greeble-modal__actions`, `.greeble-checkbox` expose specific styling knobs.

## Copy & Paste

```html
<button class="greeble-button greeble-button--primary" hx-get="/modal/example" hx-target="#modal-root" hx-swap="innerHTML">Invite teammates</button>
<div id="modal-root" aria-live="polite"></div>
```

Return the modal partial example to hydrate the dialog. Close endpoints should respond with an empty string to remove the modal from the DOM.
