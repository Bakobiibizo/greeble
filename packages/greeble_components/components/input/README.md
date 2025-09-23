# Input Components

- **Purpose:** Collect structured data with consistent styling for text, email, select, and textarea controls.
- **Inputs:** Native attributes (`required`, `autocomplete`, etc.); error messages referenced via `aria-describedby`.
- **Outputs:** Validation endpoints return updated field fragments (`hx-swap="outerHTML"`).
- **Dependencies:** `greeble_core` tokens and component CSS for invalid state, hints, and select arrow.
- **Events:** Optional HX-Trigger payloads like `{ "greeble:validate": { "field": "email" } }`.
- **Accessibility:** Visible labels, hint text, and `role="alert"` errors ensure screen readers receive updates.
