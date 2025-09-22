# Landing Page Demo

A single-page FastAPI example that wires every Greeble component into realistic product flows. Each section mirrors a production use-case and includes acceptance criteria so teams can test behavior end-to-end.

## Run the demo

Prerequisites: the repo uses `uv` to manage the environment defined in `pyproject.toml`.

```bash
uv run uvicorn examples.site.landing:app --reload --port 8045
```

Then open http://127.0.0.1:8045/ to view the landing experience. The server auto-reloads on code changes.

## Acceptance checklist

Mark each row when the described behavior passes during manual or automated runs.

| Section | Scenario | Pass when… |
| --- | --- | --- |
| Sign In Hub | Email validation, sign-in toast, and modal preview | `POST /auth/validate` swaps the email group with inline errors (400 on invalid), `POST /auth/sign-in` clears the group and emits a success toast, `POST /newsletter/subscribe` shows the info toast, and `GET /modal/example` still previews the onboarding modal |
| Product Search | Input and palette update together | Default results render from the catalog; `POST /palette/search` rewrites the listbox with matches (including empty/error states) and selecting an option `POST /palette/select` refreshes the detail panel |
| Featured Data | Table sorts and paginates | `GET /table?page=N&sort=field:dir` replaces `<tbody>` rows and the response includes the `featured-table-updated` HX-Trigger header |
| Product Tabs | Tabs lazy-load content | Default tab loads via `hx-trigger="load"`; clicking any `[role=tab]` fetches `/tabs/{key}`, updates the panel, and toggles `aria-selected` |
| Promotions Drawer | Drawer swaps in/out cleanly | `GET /drawer/open` injects the overlay partial, while `GET /drawer/close` clears `#drawer-root`; close controls remain focusable |
| Infinite Updates | Feed appends items | Sentinel `GET /list` (revealed) appends `<li>` items with `hx-swap="beforeend"`; the manual button does the same |
| Live Status | SSE pushes OOB fragments | `/stream` sends SSE messages every ~2s with `hx-swap-oob="true"` fragments targeting `#live-clock` |

## Automated coverage

- `tests/test_landing_demo.py` exercises the HTMX endpoints with `TestClient`.
- Run everything with `uv run pytest tests/test_landing_demo.py` (or `uv run pytest` to include the rest of the suite).

The tests align with the acceptance checklist so regressions surface quickly.
