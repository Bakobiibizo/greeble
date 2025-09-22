# Command Palette

- **Purpose:** Keyboard-friendly search that triggers commands with HTMX requests.
- **Structure:** `palette.html` renders the search form, results area, and detail preview. Results are
  swapped into `#palette-results`; selections replace `#palette-detail`.
- **Endpoints:** `POST /palette/search` returns the results list (listbox). `POST /palette/select`
  returns the detail panel for the chosen command.
- **Events:** Emit HX triggers such as `{"greeble:palette:select": {"command": "open-project"}}` if
  other UI elements should react to palette selections.
- **Accessibility:** Form is `role="search"`; results use `role="listbox"`/`role="option"`. Each
  option toggles `aria-selected`.
- **Theming:** Override `.greeble-palette__result`, `.greeble-palette__detail`, or the surrounding
  layout classes to fit your design system.
