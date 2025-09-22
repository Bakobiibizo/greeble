# Stepper

- Purpose: Multi-step wizard.
- Inputs: Step key and form data.
- Endpoints: GET /stepper/{stepKey}; POST /stepper/{stepKey}
- Events: `greeble:stepper:change`.
- Accessibility: Announce step changes; disable invalid next.
- States: Per-step loading/validation.
- Theming hooks: Step indicators; panels.

## Copy & Paste Usage

Markup:

```html
<nav class="greeble-stepper" aria-label="Steps">
  <button type="button" aria-current="step" hx-get="/stepper/one" hx-target="#stepper-panel" hx-swap="innerHTML">Step One</button>
  <button type="button" hx-get="/stepper/two" hx-target="#stepper-panel" hx-swap="innerHTML">Step Two</button>
</nav>
<div id="stepper-panel" role="region" aria-live="polite"></div>
```

Server returns a fragment for the requested step (200 OK). You may emit `HX-Trigger` headers like `{"greeble:stepper:change": {"step": "two"}}`. For validation flows, return 400 with the updated group or panel content.
