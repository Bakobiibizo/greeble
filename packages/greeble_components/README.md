# greeble_components

- **Purpose:** Source-of-truth HTML/CSS snippets to be copied into applications by the CLI.
- **Inputs:** None directly; components define expected data attributes and server endpoints.
- **Outputs:** Component HTML partials and associated CSS assets.
- **Dependencies:** HTMX (front-end). Optional Hyperscript. CSS variables from `greeble_core`.

Each component folder provides:
- `templates/*.html` (trigger markup and partials)
- `static/*.css` (component styles)
- `README.md` (contract: inputs, endpoints, events, accessibility)
