# Codex Agent Notes – greeble

## TODO (2025-09-21)
- [x] Build landing page FastAPI demo at `examples/site/landing.py` with combined sections and HTMX endpoints.
- [x] Document landing demo usage and acceptance criteria in `examples/site/README.md`.
- [x] Add automated tests covering landing demo flows (modal, tabs, table, drawer, palette, form, list, SSE stubs).

## Notes (2025-09-21)
- Landing hero now operates as an email sign-in flow (`/auth/validate`, `/auth/sign-in`) with newsletter opt-in emitting info toasts via `/newsletter/subscribe`.
- Drawer overlay renders custom markup (`DRAWER_PARTIAL`) so the promotions panel anchors to the right with backdrop and close affordances.

## TODO (2025-09-22)
- [x] Review architecture alignment between docs/architecture.md and current implementation.
- [x] Enumerate outstanding implementation gaps tied to roadmap milestones.

## Notes (2025-09-22)
- Component templates and CSS remain high-level placeholders aside from modal/drawer; landing demo hosts the only production-level flows.
- FastAPI adapter helpers live in src/greeble/adapters/fastapi.py; Django/Flask adapters and CLI scaffolds are still placeholders.
- Docs site, Tailwind preset, and Hyperscript packages exist only as stubs; no generated documentation yet.

## TODO (2025-09-22) – Upcoming
- [x] Ship v0.1 component vertical slice (buttons → table) with production markup/docs/tests.
- [ ] Implement CLI copy workflow + docs site live examples.
- [ ] Build out Django/Flask adapter parity after tooling lands.

## Notes (2025-09-22 – late)
- Updated TemplateResponse usage across tests/adapters to Starlette request-first signature; `uv run dev test` now runs clean.
- Landing demo now imports component CSS, uses refreshed button/input/modal/table markup, and exposes HTMX endpoints for table search/export/details and toast dismissal.
- Added mypy exclude for demo folders and annotated pytest fixtures so `uv run dev check` completes without the fastapi-demo package warning.
- Customer-facing docs expanded: README quick-start, component catalogue, and individual component
  guides now document server contracts and out-of-band patterns.
- Upgraded remaining components (drawer, dropdown, palette, stepper, tabs, infinite list, validated
  form) with production markup, CSS, docs, and tests mirroring the landing demo flows.
- Landing demo now consumes the refreshed component templates (dropdown, palette, stepper, validated
  form, drawer, infinite list) with matching HTMX endpoints and out-of-band toasts.
- Implemented greeble CLI (`list`, `add`, `sync`, `remove`, `doctor`) with manifest-driven copy
  logic, documentation, and tests; README and docs now include a detailed CLI + adapter walkthrough.

## TODO (2025-09-23)
- [x] Add `greeble new` CLI starter scaffold with FastAPI endpoints.
- [x] Document `greeble new` usage and tests once implementation lands.

## Notes (2025-09-23)
- Added `greeble new` command to scaffold FastAPI starter projects with endpoint skeletons, docs opt-in, and dry-run/force modes.
- CLI and docs refreshed to cover starter workflows; regression tests confirm docs copy and HTMX endpoint coverage.
