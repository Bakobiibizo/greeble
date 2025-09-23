# Greeble Progress Report – 2025-09-23

## Snapshot
- Component markup, CSS, and docs for the core catalog (buttons through infinite list, validated form, palette, toasts) ship from `packages/greeble_components/` and are exercised by the FastAPI landing demo and pytest suites.
- The CLI now covers `list`, `add`, `sync`, `remove`, `doctor`, and the new `greeble new` starter scaffold, giving teams an end-to-end FastAPI bootstrap story.
- FastAPI adapter helpers (`src/greeble/adapters/fastapi.py`) support HTMX detection, partial rendering, and trigger headers; they are used across tests and demos.
- Major architecture planks still outstanding: Django/Flask adapter parity, Tailwind preset export, Hyperscript bundle, docs site, theme tooling, and accessibility/visual regression automation.

## Area Status

| Area | Architecture Intent | Current Status (2025-09-23) | Gaps / Follow-ups |
| --- | --- | --- | --- |
| Component library | Ship copy/paste HTML, partials, CSS, docs for catalog in §15; declare contracts in manifest | ✅ `packages/greeble_components/` contains full markup + docs; manifest enumerates endpoints; vertical slice used in demos/tests | Keep manifest and component docs in sync as new patterns land; add remaining roadmap components (0.4+)
| Design tokens (`greeble_core`) | Provide CSS variables + utilities (Section 6) | ✅ `packages/greeble_core/assets/css/greeble-core.css` distributed and imported by demos | Document override patterns; consider packaging tokens as static asset in CLI starter
| Hyperscript snippets | Optional behavior package (§5.1) | ⚠️ Only README placeholder in `packages/greeble_hyperscript`; components reference inline `.hyperscript.html` files | Extract shared scripts into publishable bundle or clarify per-component inclusion story
| Tailwind preset | Map tokens to Tailwind theme (§6.3) | ⚠️ Placeholder README in `packages/greeble_tailwind_preset`; no actual preset export | Implement `preset.cjs`/`index.js`, add tests/docs, wire into CLI starter instructions
| Adapters | Django/Flask parity, middleware, helpers (§8) | ✅ FastAPI helper implemented in `src/greeble/adapters/fastapi.py`; ⚠️ packages/adapters/{django,flask} remain stubs | Build real Django template tags, middleware, Flask blueprint; deduplicate adapter code between `src/` and `packages/adapters`
| CLI tooling | Copy components, manage tokens, scaffold projects (§9) | ✅ Commands: `list/add/sync/remove/doctor/new`; tests in `tests/test_cli.py`; manifest-driven copy plan | Still missing `theme init` / Tailwind wiring; add adapter-aware scaffolds (Django/Flask) once adapters mature; review packaging of starter templates
| Documentation | Docs site with live examples (§17) | ✅ README, CLI guide, component docs updated; ⚠️ `docs/site/` is placeholder, no generated site | Build docs site (mkdocs/astro) with live demos and “view source”; automate publish workflow
| Examples | FastAPI, Django, Flask demos (§5.1, §14) | ✅ `examples/site/landing.py` & `examples/fastapi-demo` cover full flows; ⚠️ `examples/django-demo` and `examples/flask-demo` are README-only | Implement framework demos after adapters; ensure CLI starter aligns with example structure
| Testing & QA | Playwright, axe-core, contract tests (§14) | ✅ Pytest suites for components, CLI, landing demo; coverage for HTMX endpoints | Add accessibility (axe) and browser snapshot tests; integrate CI gating; expand contract tests for adapters once parity achieved
| Distribution | Packages per architecture layout (§5.1) | ⚠️ Mixed structure: runtime code in `src/`, placeholders under `packages/adapters/`; starter templates under `src/greeble_cli/templates/` | Reconcile packaging strategy before publishing (decide on single vs multi-package distribution); ensure MANIFEST.in / pyproject include starter assets

## Near-Term Priorities
- Build Django and Flask adapter implementations (template tags, middleware/blueprint) to unlock multi-framework parity promised in the architecture.
- Implement Tailwind preset exports plus CLI-driven theme/init workflow so teams can adopt tokens quickly.
- Stand up the docs site with live examples and “view source” tooling; fold landing demo content into the site.
- Add accessibility (axe) and browser snapshot automation to align with the testing strategy defined in §14.
- Clarify Hyperscript packaging: either provide a distributable bundle or document per-component inclusion, then ensure CLI/new scaffold wires it correctly.
- Finalize distribution layout (src vs packages directories) ahead of publishing to PyPI to avoid drift between architecture and shipped artifacts.

## Test Assessment
- **Unit & integration coverage:** Pytest suites exercise CLI commands (`tests/test_cli.py`), FastAPI adapter helpers, and end-to-end component flows under FastAPI/Flask via `tests/components/`. Landing demo tests validate HTMX routes and out-of-band swaps.
- **Gaps:** No automated coverage for Django adapter placeholders, Tailwind preset, or Hyperscript bundle. Accessibility checks (axe), visual regression (Playwright/pytest-playwright), and multi-browser testing are pending. Starter scaffold currently validated via CLI tests only—no smoke test ensuring generated projects run.
- **Tooling:** `uv` orchestrates env/test commands; no CI pipeline configured yet to gate merges on the current suite. Need coverage reporting to track progress as new frameworks/tests are added.
- **Next steps:** Expand tests once Django/Flask adapters land, introduce docs-site smoke tests, add accessibility and snapshot tooling, and wire these into CI alongside coverage metrics.

## Longer-Term Follow-ups
- Extend `greeble new` to generate Django/Flask starter templates once adapters are ready; consider presetting Tailwind integration.
- Revisit roadmap items beyond v0.3 (file upload, data grid, date picker) and update manifest/docs accordingly.
- Explore optional `greeble theme init` CLI command once Tailwind preset and design token tooling are implemented.
- Document security patterns (CSRF, rate limiting) per framework as called out in §12.
