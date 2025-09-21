# Table

- Purpose: Sortable, pageable table.
- Inputs: Query params `page`, `sort`.
- Endpoints: GET /table?page=<n>&sort=<field>:<dir>
- Events: `greeble:table:sorted`, `greeble:table:paged`.
- Accessibility: Caption; scope attributes; summaries.
- States: Empty, loading, error; sorted indicators.
- Theming hooks: Table borders, row hovers.
