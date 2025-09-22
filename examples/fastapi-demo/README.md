# FastAPI Demo

This demo renders all Greeble components and showcases different endpoint types for HTMX:

- Full-page routes that serve component trigger markup and targets
- Partial endpoints that return HTML fragments
- Validation endpoints that return 400 status with partials
- Out-of-band (OOB) fragments to update multiple zones
- SSE (Server-Sent Events) streaming OOB fragments

## Run the demo

Prerequisites: `uv` is used to manage the dev environment per the project `pyproject.toml`.

Option A (recommended):

```
uv run python examples/fastapi-demo/main.py
```

Option B:

```
uv run uvicorn examples.fastapi-demo.main:app --reload
```

Then open http://127.0.0.1:8000/ in your browser.

## Routes

- `/` Index with links to each component page

- Component pages (full page):
  - `/demo/button` → serves `button.html`
  - `/demo/input` → serves `input.html`
  - `/demo/dropdown` → serves `dropdown.html`
  - `/demo/tabs` → serves `tabs.html`
  - `/demo/table` → serves `table.html`
  - `/demo/modal` → serves `modal.html`
  - `/demo/toast` → serves `toast.root.html`
  - `/demo/drawer` → serves `drawer.html`
  - `/demo/palette` → serves `palette.html`
  - `/demo/stepper` → serves `stepper.html`
  - `/demo/infinite-list` → serves `infinite-list.html`

- Partial endpoints (HTMX):
  - `GET /tabs/{tabKey}` → returns `<section>Content for {tabKey}</section>`
  - `GET /table/rows?page=&sort=` → returns `<tr>` rows
  - `GET /modal/example` → returns `modal.partial.html`
  - `GET /modal/close` → returns empty fragment
  - `POST /modal/submit` → returns OOB toast
  - `POST /notify` → returns OOB toast
  - `GET /drawer/open` → returns `drawer.partial.html`
  - `GET /drawer/close` → returns empty fragment
  - `POST /palette/search` → returns listbox results
  - `GET /stepper/{stepKey}` → returns step content
  - `GET /list` → returns infinite list item

- Streaming endpoints:
  - `/demo/sse` → page that connects to `/stream` via HTMX SSE extension
  - `GET /stream` → SSE stream emitting OOB fragments (updates `#live-clock`)

All component templates are sourced directly from `packages/greeble_components/components/<name>/templates`.
