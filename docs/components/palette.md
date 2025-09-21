# Command Palette

- Purpose: Server-backed search with keyboard selection.
- Inputs: Form field `q`.
- Endpoints: POST /palette/search
- Events: `greeble:palette:select`.
- Accessibility: role=dialog; listbox semantics; announcements.
- States: Idle, searching, empty, results.
- Theming hooks: Input and results list.
