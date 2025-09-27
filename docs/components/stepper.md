# Stepper

- Purpose: Break complex workflows into ordered steps with server-rendered content.
- Structure: Navigation buttons (`.greeble-stepper__step`) call `hx-get` endpoints that replace the
  panel content. Use `aria-current="step"` to highlight progress.
- Endpoints: `GET /stepper/{stepKey}` for each step. Optional `POST /stepper/{stepKey}` to validate
  before continuing.
- Events: Emit `HX-Trigger: {"greeble:stepper:change": {"step": "enable"}}` or
  `{ "greeble:stepper:complete": true }` in responses.
- Accessibility: Panel is `aria-live="polite"`; steps use badges and `aria-current` for clarity.
- Theming hooks: `.greeble-stepper__badge`, `.greeble-stepper__step[aria-current]`, and
  `.greeble-stepper__panel`.

## Include in template

```jinja
{% include "greeble/stepper.html" %}
```

## Copy & Paste

```html
<section class="greeble-stepper" aria-labelledby="stepper-heading">
  <header class="greeble-stepper__header">
    <h2 id="stepper-heading" class="greeble-heading-2">Launch readiness checklist</h2>
    <p class="greeble-stepper__description">Complete each milestone before launch day.</p>
  </header>
  <ol class="greeble-stepper__list" role="list">
    <li class="greeble-stepper__item">
      <button class="greeble-stepper__step" type="button" data-step="plan" aria-current="step"
              hx-get="/stepper/plan" hx-target="#stepper-panel" hx-swap="innerHTML">
        <span class="greeble-stepper__badge">1</span>
        <span class="greeble-stepper__meta">
          <strong>Plan launch</strong>
          <small>Outline timeline, owners, and messaging.</small>
        </span>
      </button>
    </li>
    <!-- Additional steps -->
  </ol>
  <div id="stepper-panel" class="greeble-stepper__panel" role="region" aria-live="polite"
       hx-get="/stepper/plan" hx-trigger="load" hx-target="this" hx-swap="innerHTML">
    <p>Loading step…</p>
  </div>
</section>
```

Example step content:

```html
<section class="greeble-stepper__content" data-step="plan">
  <h3 class="greeble-heading-3">Plan launch</h3>
  <p>Confirm the launch checklist and share timelines with stakeholders.</p>
  <ul class="greeble-stepper__tasks">
    <li>Align on launch date and success metrics.</li>
    <li>Draft customer messaging and enablement docs.</li>
    <li>Schedule dry run across teams.</li>
  </ul>
  <div class="greeble-stepper__actions">
    <button class="greeble-button" type="button" hx-get="/stepper/intro" hx-target="#stepper-panel" hx-swap="innerHTML">
      Back
    </button>
    <button class="greeble-button greeble-button--primary" type="button"
            hx-get="/stepper/enable" hx-target="#stepper-panel" hx-swap="innerHTML">
      Continue to enablement
    </button>
  </div>
</section>
```

Handle validation by returning the same step content with inline error messaging and an HTTP 400
status.

## Keyboard map

- Arrow Up/Down or Left/Right – Move focus between step buttons (depending on layout).
- Enter/Space – Activate the focused step; fetch the panel content for that step.
- Tab / Shift+Tab – Move between stepper controls and the panel region.

## Response matrix

- GET /stepper/{stepKey}
  - 200 OK — returns panel content for requested step
  - Headers: `HX-Trigger: {"greeble:stepper:change": {"step": "<stepKey>"}}`

- POST /stepper/{stepKey}
  - 200 OK — returns next step content; may emit `{ "greeble:stepper:complete": true }` when finished
  - 400 Bad Request — returns same step content with inline errors; keep `aria-live` announcements

## View source

- Template: [stepper.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/stepper/templates/stepper.html)
- Partial: [stepper.partial.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/stepper/templates/stepper.partial.html)
- Styles: [stepper.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/stepper/static/stepper.css)
