# Greeble Roadmap

This living roadmap outlines the planned work for Greeble. It’s organized as Now / Next / Later and backed by milestone groupings. For current status, see `docs/progress.md`.

## Now (in progress)

- Centralize HTMX-aware response helpers across FastAPI, Django, and Flask (headers, CSRF utilities, message-to-toast middleware).
- Ship Django template tags/middleware and a Flask blueprint so adapters hit feature parity with the FastAPI helpers.
- Align demos and starters on the canonical asset pipeline (shared head markup, icons, Tailwind preset wiring) and document override patterns.
- Finalize component contracts (markup requirements, events, tokens) with validation tooling baked into CI.

## Next (queued)

- Bundle client behaviour (`greeble.js`) that registers Hyperscript snippets, exposes toast/focus helpers, and hooks HTMX lifecycle events.
- Expand CLI workflows (`greeble new`, `sync`, `doctor`) with post-scaffold diagnostics, diff-aware sync, and framework-specific checks.
- Land accessibility-first component updates (modal/dialog focus management, tabs roving tabindex, toast live regions) and enforce through automated tests.
- Establish Playwright + axe-core pipelines for component snapshots and smoke tests across framework adapters.

## Later (backlog)

- Add additional components beyond v0.3 (file upload, data grid, date picker); update manifest/docs accordingly.
- Explore optional advanced `greeble theme init` tooling after preset export and tokens workflow stabilize.
- Document security patterns (CSRF, rate limiting) per framework.

## Milestones (targeted sequencing)

- 0.0.9
  - Shared HTMX response helper (`set_htmx_headers`) adopted across adapters and demos.
  - Django CSRF tag/macro, toast middleware, and Flask blueprint with namespaced partials delivered.
  - Tailwind preset/token docs refreshed; starters consume canonical head markup and asset pipeline.
  - Component contracts authored with automated validation covering modal, drawer, tabs, toast, and form flows.

- 0.0.10
  - Client bundle (`greeble.js`) shipping hyperscript behaviours, focus/scroll helpers, and HTMX hooks.
  - CLI polish: post-scaffold doctor, diff-aware sync, richer doctor diagnostics published.
  - Accessibility automation landed (Playwright + axe-core) covering modal/dialog, tabs, toast, and form components.
  - Visual regression baselines and starter smoke tests executed across FastAPI/Django/Flask apps.

- 0.0.11+
  - Performance work (minified CSS/JS bundles, swap-granularity guidance, streaming patterns) documented and enforced.
  - Security guidance expanded (CSP recipes with Hyperscript, HTMX idempotency patterns, escape auditing).
  - Additional components (file upload, data grid, date picker) queued once foundations stabilize.

## How to follow along

- Progress snapshots and gap analysis live in `docs/progress.md`.
- Component contracts and examples are documented under `docs/components/`.
- CLI usage and adapter notes are in `docs/cli.md` and `docs/adapters.md`.

## Contributing

We welcome contributions that align with the “Now” and “Next” items above. If you’re interested in a “Later” item, please open an issue to discuss scope before starting. Use Conventional Commits and run `uv run dev check` locally before opening a PR.

