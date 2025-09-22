# Table

- Purpose: Display tabular data with HTMX-backed sorting, filtering, and pagination.
- Structure: `.greeble-table-shell` wraps header, actions, table container, and pagination. `tbody#table-body` hydrates via `hx-get` calls.
- Endpoints: `GET /table` returns row partials; optional `POST /table/search` or `POST /table/export` extend interactions.
- Sorting: Header buttons use `hx-get="/table?page=1&sort=field:dir"` and swap the partial into `#table-body`.
- Accessibility: Table keeps native semantics with `<th scope="row">`; status chips include visually hidden text where necessary; live updates announce via `aria-live="polite"` on the tbody.
- Events: Servers can set `HX-Trigger: {"greeble:table:update": {"page": 2}}` to coordinate other components.
- Theming hooks: Override `.greeble-table__status--*` colors or container background to match brand palette.

## Copy & Paste

```html
<section class="greeble-table-shell">
  <div class="greeble-table__container">
    <table class="greeble-table">
      <thead>…</thead>
      <tbody id="table-body" hx-get="/table?page=1" hx-trigger="load" hx-target="this" hx-swap="innerHTML"></tbody>
    </table>
  </div>
  <nav class="greeble-pagination" aria-label="Pagination">
    <button class="greeble-button" type="button" hx-get="/table?page=1" hx-target="#table-body" hx-swap="innerHTML">1</button>
    <button class="greeble-button" type="button" hx-get="/table?page=2" hx-target="#table-body" hx-swap="innerHTML">2</button>
  </nav>
</section>
```
