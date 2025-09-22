# Modal

- Purpose: Dialog with focus trap and backdrop.
- Inputs: Trigger (hx-get), inner form inputs.
- Endpoints: GET /modal/example, GET /modal/close, POST /modal/submit
- Events: `greeble:modal:open`, `greeble:modal:close`.
- Accessibility: role=dialog; aria-modal; focus management.
- States: Open, closing, error in form body.
- Theming hooks: Panel, backdrop classes; tokens.

## Copy & Paste Usage

Trigger markup:

```html
<button class="greeble-button" hx-get="/modal/example" hx-target="#modal-root" hx-swap="innerHTML">Open Modal</button>
<div id="modal-root" aria-live="polite"></div>
```

Returned partial contains a body with a sample form that posts to `/modal/submit` and close controls that `hx-get` `/modal/close` to clear the root. Servers can return an out-of-band toast on submit success and/or set `HX-Trigger` headers (e.g., `{"greeble:modal:close": true}`).
