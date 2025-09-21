# Stepper (Placeholder)
- **Purpose:** Multi-step wizard.
- **Inputs:** Step key; form data.
- **Outputs:** Partial per step; submit results.
- **Dependencies:** HTMX; greeble_core.
- **Endpoints:** GET /stepper/{stepKey}; POST /stepper/{stepKey}
- **Events:** `greeble:stepper:change`
- **Accessibility:** Announce step changes; disable next when invalid.
