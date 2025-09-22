# Table
- **Purpose:** Present paginated datasets with HTMX-driven sorting, searching, and actions.
- **Inputs:** Query params such as `page`, `sort`, `q`; responses return `<tbody>` fragments.
- **Outputs:** `table.html` base markup + `table.partial.html` row template.
- **Dependencies:** HTMX; `greeble_core` tokens; component CSS for layout, statuses, and pagination controls.
- **Endpoints:** `GET /table` (rows), optional `POST /table/search`, `POST /table/export`.
- **Events:** Emit `greeble:table:sorted` or `greeble:table:paged` via HX-Trigger headers when swaps complete.
- **Accessibility:** Caption (or visually hidden caption) describes dataset; `<th scope="row">` identifies rows; live updates announced via `aria-live` on tbody.
