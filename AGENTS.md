# Codex Agent Notes – greeble

## TODO (2025-09-21)
- [x] Build landing page FastAPI demo at `examples/site/landing.py` with combined sections and HTMX endpoints.
- [x] Document landing demo usage and acceptance criteria in `examples/site/README.md`.
- [x] Add automated tests covering landing demo flows (modal, tabs, table, drawer, palette, form, list, SSE stubs).

## Notes (2025-09-21)
- Landing hero now operates as an email sign-in flow (`/auth/validate`, `/auth/sign-in`) with newsletter opt-in emitting info toasts via `/newsletter/subscribe`.
- Drawer overlay renders custom markup (`DRAWER_PARTIAL`) so the promotions panel anchors to the right with backdrop and close affordances.
