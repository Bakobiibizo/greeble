# Greeble Roadmap

This living roadmap outlines the planned work for Greeble. It’s organized as Now / Next / Later and backed by milestone groupings. For current status, see `docs/progress.md`.

## Now (in progress)

- Build Django and Flask adapter implementations (template tags, middleware/blueprint) to reach parity with FastAPI adapter.
- Implement Tailwind preset exports and a CLI-driven theme/init workflow so teams can adopt tokens quickly.
- Stand up the docs site with live examples and “view source”; fold the landing demo content into the site.
- Add accessibility (axe) and browser snapshot automation to align with testing strategy.
- Clarify Hyperscript packaging strategy (bundle vs per-component inclusion) and wire into CLI scaffolds.
- Finalize distribution layout (src vs packages/) ahead of publishing to PyPI; ensure packaging includes starter assets.

## Next (queued)

- Expand tests once Django/Flask adapters land; introduce docs-site smoke tests.
- Integrate CI gating with coverage metrics; add accessibility checks and visual regression to CI.
- Reconcile adapter code between `src/greeble/adapters/` and `packages/adapters/` to avoid duplication.
- Document override patterns for `greeble_core` tokens and consider packaging tokens as static assets in the CLI starter.
- Implement Tailwind preset export deliverables (`preset.cjs`/`index.js`) and add tests/docs; wire into `greeble new`.

## Later (backlog)

- Extend `greeble new` to generate Django/Flask starter templates once adapters are ready; preset Tailwind integration.
- Add additional components beyond v0.3 (file upload, data grid, date picker); update manifest/docs accordingly.
- Explore optional `greeble theme init` CLI command once Tailwind preset and token tooling are complete.
- Document security patterns (CSRF, rate limiting) per framework.

## Milestones (targeted sequencing)

- v0.2
  - Django + Flask adapter parity (min viable template tags, middleware/blueprint, examples)
  - Tailwind preset initial export wired to CLI; docs for token mapping
  - Docs site skeleton with live examples for core components

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

