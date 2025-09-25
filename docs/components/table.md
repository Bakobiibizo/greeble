# Table

- Purpose: Display tabular data with HTMX-backed sorting, filtering, and pagination.
- Structure: `.greeble-table-shell` wraps header, actions, table container, and pagination. `tbody#table-body` hydrates via `hx-get` calls.
- Endpoints: `GET /table` returns row partials; optional `POST /table/search`, `POST /table/export`,
  `GET /table/accounts/{slug}`, `POST /table/accounts/{slug}/remind`,
  `POST /table/accounts/{slug}/escalate`, and `DELETE /table/accounts/{slug}` power secondary
  actions.
- Sorting: Header buttons use `hx-get="/table?page=1&sort=field:dir"` and swap the partial into `#table-body`.
- Accessibility: Table keeps native semantics with `<th scope="row">`; status chips include visually hidden text where necessary; live updates announce via `aria-live="polite"` on the tbody.
- Events: Servers can set `HX-Trigger: {"greeble:table:update": {"page": 2}}` after pagination,
  `greeble:table:view` after loading details, `greeble:table:remind`/`escalate`/`archive` after row
  actions, and `greeble:toast` when exports queue background jobs.
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

## Server contract

- `GET /table` accepts `page` (1-indexed) and `sort` (`field:direction`) parameters and returns the
  `<tr>` collection. When no rows are available, return a single `<tr><td colspan="…">No results.</td></tr>`.
- `POST /table/search` filters data and should respond with the same partial markup. Include
  `HX-Trigger` payloads when you need to update UI state (for example, surface the number of
  matches).
- `POST /table/export` demonstrates returning an out-of-band toast while keeping the table intact.
- Row actions (`view`, `remind`, `escalate`, `archive`) return either an out-of-band toast or an
  empty fragment that HTMX uses to manipulate the matching row. Use descriptive `HX-Trigger`
  payloads so other UI (badge counts, notifications) can react.

## Keyboard map

- Arrow Up/Down – Navigate focus between interactive controls in the table (e.g. action buttons).
- Tab / Shift+Tab – Move between focusable elements; header sort buttons should be reachable.
- Enter / Space – Activate focused button, including header sort controls and row actions.

## Response matrix

- GET /table?page={n}&sort={field}:{dir}
  - 200 OK — returns `<tr>` rows for requested page and sort
  - Headers: `HX-Trigger: {"greeble:table:update": {"page": n, "sort": "field:dir"}}`

- POST /table/search { q }
  - 200 OK — returns filtered `<tr>` rows or a single `<tr><td colspan="…">No accounts match…</td></tr>` when empty
  - Headers: `HX-Trigger: {"greeble:table:update": {"query": "<q>", "results": <int>}}`

- POST /table/export
  - 200 OK — returns out-of-band toast only
  - Headers: `HX-Trigger: {"greeble:toast": {"level": "info"}}`

- GET /table/accounts/{slug}
  - 200 OK — returns out-of-band toast only
  - Headers: `HX-Trigger: {"greeble:table:view": {"org": "<org>"}}`

- POST /table/accounts/{slug}/remind
  - 200 OK — returns out-of-band toast only
  - Headers: `HX-Trigger: {"greeble:table:remind": {"org": "<org>"}}`

- POST /table/accounts/{slug}/escalate
  - 200 OK — returns out-of-band toast only
  - Headers: `HX-Trigger: {"greeble:table:escalate": {"org": "<org>"}}`

- DELETE /table/accounts/{slug}
  - 200 OK — returns out-of-band toast only; client removes row on success
  - Headers: `HX-Trigger: {"greeble:table:archive": {"org": "<org>"}}`

## View source

- Template: [table.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/table/templates/table.html)
- Partial: [table.partial.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/table/templates/table.partial.html)
- Styles: [table.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/table/static/table.css)
