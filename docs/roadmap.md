# Greeble Roadmap

This living roadmap outlines the planned work for Greeble. It’s organized as Now / Next / Later and backed by milestone groupings. For current status, see `docs/progress.md`.

## Now (in progress)

- Deliver Django template tags and middleware to hit parity with FastAPI helpers; begin porting the blueprint pattern for Flask.
- Implement Tailwind preset exports (`preset.cjs` / `index.js`) and land a CLI-driven `theme init` workflow so starters consume tokens out of the box.
- Finish folding the landing demo into the MkDocs site: promote the new minimal landing as home, add live component examples with “view source,” and align shared assets (favicons, icons) across starters and demos.
- Unify styling across the FastAPI, Django, and Flask demos so they inherit the canonical look and feel from `examples/site/landing.py`.
- Clarify the Hyperscript distribution story (bundle vs per-component) and update CLI scaffolds and docs to match the chosen approach.
- Lock the distribution layout (`src/` vs `packages/`) and packaging manifest so starter assets and adapters publish cleanly to PyPI.

## Next (queued)

- Backfill automated coverage once Django/Flask adapters land: adapter contract tests, docs-site smoke tests, and a generated starter boot/run check.
- Integrate CI gating with coverage metrics and introduce accessibility (axe) plus visual regression (Playwright) automation.
- Reconcile adapter code between `src/greeble/adapters/` and `packages/adapters/` to avoid duplication.
- Document override patterns for `greeble_core` tokens and ship starter-friendly guidance (consider packaging tokens as static assets).
- Extend `greeble new` with Django and Flask starter blueprints once adapters stabilize.

## Later (backlog)

- Add additional components beyond v0.3 (file upload, data grid, date picker); update manifest/docs accordingly.
- Explore optional advanced `greeble theme init` tooling after preset export and tokens workflow stabilize.
- Document security patterns (CSRF, rate limiting) per framework.

## Milestones (targeted sequencing)

- v0.2
  - Django + Flask adapter parity (min viable template tags, middleware/blueprint, examples)
  - Tailwind preset initial export wired to CLI; docs for token mapping and starter consumption
  - Docs site home unified with landing demo, live component examples, and “view source” affordances

- v0.3
  - Accessibility (axe) + visual regression automation (Playwright) with CI gating
  - Hyperscript packaging clarified and integrated in CLI/new scaffold
  - Distribution layout finalized for publishing; starter assets packaged

- v0.4+
  - Additional components: file upload, data grid, date picker
  - Expand framework docs (security patterns per framework)
  - Broaden adapter contract tests and sample apps

## How to follow along

- Progress snapshots and gap analysis live in `docs/progress.md`.
- Component contracts and examples are documented under `docs/components/`.
- CLI usage and adapter notes are in `docs/cli.md` and `docs/adapters.md`.

## Contributing

We welcome contributions that align with the “Now” and “Next” items above. If you’re interested in a “Later” item, please open an issue to discuss scope before starting. Use Conventional Commits and run `uv run dev check` locally before opening a PR.

