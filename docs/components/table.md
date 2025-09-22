# Table

- Purpose: Sortable, pageable table.
- Inputs: Query params `page`, `sort`.
- Endpoints: GET /table?page=<n>&sort=<field>:<dir>
- Events: `greeble:table:sorted`, `greeble:table:paged`.
- Accessibility: Caption; scope attributes; summaries.
- States: Empty, loading, error; sorted indicators.
- Theming hooks: Table borders, row hovers.

## Copy & Paste Usage

Include the table markup and wire your endpoint at `/table`:

```html
<table class="greeble-table">
  <caption>Example Table</caption>
  <thead>
    <tr>
      <th scope="col">
        <button type="button" hx-get="/table?page=1&sort=col:asc" hx-target="#table-body" hx-swap="innerHTML">Col ▲</button>
        <button type="button" hx-get="/table?page=1&sort=col:desc" hx-target="#table-body" hx-swap="innerHTML">Col ▼</button>
      </th>
    </tr>
  </thead>
  <tbody id="table-body" hx-get="/table?page=1" hx-trigger="load" hx-swap="innerHTML"></tbody>
</table>
<nav class="greeble-pagination" aria-label="Pagination">
  <button type="button" hx-get="/table?page=1" hx-target="#table-body" hx-swap="innerHTML">1</button>
  <button type="button" hx-get="/table?page=2" hx-target="#table-body" hx-swap="innerHTML">2</button>
</nav>
```

Server returns a `<tr>...</tr>` fragment (200 OK). You may include `HX-Trigger` headers to emit `greeble:table:sorted` or `greeble:table:paged` events.
