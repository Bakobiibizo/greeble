# Table (Placeholder)
- **Purpose:** Sortable, pageable table with row actions.
- **Inputs:** Query params `page`, `sort`.
- **Outputs:** Table body partial.
- **Dependencies:** HTMX; greeble_core.
- **Endpoints:** GET /table?page=<n>&sort=<field>:<dir>
- **Events:** `greeble:table:sorted`, `greeble:table:paged`
- **Accessibility:** Caption recommended; scope on headers.
