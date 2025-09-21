# Command Palette (Placeholder)
- **Purpose:** Search input with server-backed results.
- **Inputs:** Form input `q`.
- **Outputs:** Result list partial.
- **Dependencies:** HTMX; greeble_core.
- **Endpoints:** POST /palette/search
- **Events:** `greeble:palette:select`
- **Accessibility:** role=dialog; listbox semantics for results.
