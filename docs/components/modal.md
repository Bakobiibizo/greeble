# Modal

- Purpose: Dialog with focus trap and backdrop.
- Inputs: Trigger (hx-get), inner form inputs.
- Endpoints: GET /modal/example, GET /modal/close, POST /modal/submit
- Events: `greeble:modal:open`, `greeble:modal:close`.
- Accessibility: role=dialog; aria-modal; focus management.
- States: Open, closing, error in form body.
- Theming hooks: Panel, backdrop classes; tokens.
