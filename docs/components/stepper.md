# Stepper

- Purpose: Multi-step wizard.
- Inputs: Step key and form data.
- Endpoints: GET /stepper/{stepKey}; POST /stepper/{stepKey}
- Events: `greeble:stepper:change`.
- Accessibility: Announce step changes; disable invalid next.
- States: Per-step loading/validation.
- Theming hooks: Step indicators; panels.
