# Stepper

- **Purpose:** Guide users through a multi-step wizard with clear progress indicators.
- **Structure:** `stepper.html` renders the navigation list and the content panel. Each step button
  fetches content into `#stepper-panel` via HTMX.
- **Endpoints:**
  - `GET /stepper/<stepKey>` → returns the panel fragment for that step.
  - Optional `POST /stepper/<stepKey>` → handles form submissions before advancing.
- **Events:** Emit HX triggers (e.g., `{"greeble:stepper:change": {"step": "enable"}}`) when steps
  change or complete.
- **Accessibility:** Buttons include `aria-current="step"` for the active step; the panel is
  `aria-live="polite"`.
- **Theming:** Customize `.greeble-stepper__step`, `.greeble-stepper__badge`, and
  `.greeble-stepper__panel` to match your product styling.
