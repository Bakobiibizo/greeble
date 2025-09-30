## [0.0.8] - 2025-09-29

### other
- Refresh documentation site and landing assets (6cc2ae9)
- Expand FastAPI demo with richer HTMX samples (38daece)
- Harden Django adapter and demo integration (edddf90)
- Refresh Flask demo with Greeble components (b57660a)
- Enhance CLI starter assets and Tailwind preset (e65ddc8)
- Clean starter landing assets (2fe5a7f)

## [0.0.7] - 2025-09-26

### feat
- unify landing assets and refresh docs (c137ed0)
- minimal landing with /docs redirect; add copyable Jinja include snippets across components; logo + env-configured links; adjust starter test (a874864)
- console entry supports --host/--port/--[no-]reload and --log-level (defaults to 127.0.0.1:8050, reload on) (#11) (dc5daf1)
- src layout with greeble_starter package (#10) (c919d20)
- include Hyperscript runtime in starter and copy modal hyperscript; tests cover new assets (9830798)
- theme init --force flag; guard overwrites for preset and config; use f-string for require_path (1151531)
- add Please ask your administrator. to scaffold Tailwind config and copy preset (9554604)

### fix
- add responsive layout for landing grid (a0cc414)

### docs
- scaffold MkDocs Material site, add nav, and view-source links; dev CLI gains docs-serve/docs-build (26d60a4)

### other
- style(landing): light/dark favicons via /static/images; mount icons for demos; scaffold icons into starters; unify reduced radii (628733b)
- style(landing): establish canonical landing styles and apply across starter + examples; link canonical CSS; darken surfaces (efc5748)

## [0.0.6] - 2025-09-24

### feat
- 2/3 centered layout with 1/6 gutters; increase early-access input padding; clarify palette to customer search with examples (dd91383)

### fix
- restore spacing scale 4 to 1rem (ac83c23)

### docs
- add roadmap doc and link from README (7fbf410)

### test
- add FastAPI e2e tests for tabs render and per-tab partial endpoint (a978fa4)
- add FastAPI e2e tests for Input component (render + validation endpoint) (7b788a4)

### chore
- auto-approve merge commit message in branch-finalize with --no-edit (e0596b6)
- add template export and setup scripts (b6edf87)

## [0.0.5] - 2025-09-23

### refactor
- extract HTMX utils; preserve HX-Trigger toasts; tighten manifest library keys; demo parity + docs todos (b33e15b)

### chore
- remove partial_html from Django/Flask; enforce template-based rendering; update tests (541f996)
- changed demo to use env variables over hard coding debug=true (c465200)

## [0.0.4] - 2025-09-23

### feat
- tighten manifest validation and docs handling (4730fde)
- implement CSS tokens/utilities; feat(drawer): styles + accessible partial; chore: align with architecture docs (cf94e32)
- implement HTMX helpers (is_hx_request, HX-Trigger headers, partial_html, template_response) with tests (eae4c29)
- add initial project structure per architecture doc (1a40798)
- added rebase and create branch commands to dev tools (7fbc6cc)

### docs
- add JSON flags docs, Django/Flask adapter parity, demos, uv groups for optional deps; add templatetags and middleware (a17001a)
- add contributing guide (abe3e32)

### test
- add FastAPI e2e tests for table render and partial endpoint (paged/sorted) (ba47dda)
- add FastAPI e2e tests for form validation and submit flows (8deb687)
- add FastAPI e2e tests validating toast root and OOB toast item updates (a7614f3)
- add FastAPI e2e tests for Modal component using adapter helpers\n\n- Add python-multipart to dev deps for Form() parsing\n- Validate modal open/close and submit OOB toast flow (db2fe1d)

### chore
- conditional logic refinement (3061eff)
- remove uv.lock file (6f8e333)
- remove .windsurf folder and adding it to gitignore (2727e44)
- remove template tools from feature branch (kept in tools/template) (b504946)
- add template export and setup scripts (96bd1d0)

### other
- Delete AGENTS.md (79799ff)
- chore(release)addressing review comments in pr (897a1ba)
- finished the components and added a cli (9033f36)
- finished component implementation and landing demo (d4962d3)
- style(modal): implement modal component styles using core tokens (2b8f474)

# Changelog

## [0.0.3] - 2025-09-20

### feat
- semantic versioning + release helpers; centralize tool configs; set initial version 0.0.1\n\n- dev version current|bump <major|minor|patch> with CHANGELOG generation and annotated tags\n- dev release rc to create/push release-candidate\n- dev protect-main uses gh CLI to enable branch protection\n- Commitizen pre-commit commit-msg hook enforcing Conventional Commits\n- Configs in pyproject (ruff, mypy, pytest, commitizen)\n- Docs version set to 0.0.1 (6072fed)

### refactor
- modernize dev CLI and wire up uv entry point\n\n- Replace if-chain with match-case; add is_ci() and run_mypy_then()\n- Improve typing and docstrings; simplify ruff checks\n- Update wrapper entrypoints to call local main()\n- Add build-system (hatchling) and src/ layout packaging config\n- Configure [project.scripts] dev entry point; default dev dependency group via [tool.uv]\n- Add package __init__.py\n\nRun with: uv run dev --help (5875223)

### ci
- add GitHub Actions workflow; update pre-commit stages; make dev check treat no-tests (pytest rc=5) as success (9066908)

### chore
- centralize tool configs in pyproject (ruff, mypy, pytest); add return type to main() (65d5948)
- remove stale erasmus entrypoint and add pre-commit hook to run 'uv run dev check' (2963923)

### other
- Initial commit (fcbcabd)

## [0.0.2] - 2025-09-20

### feat
- semantic versioning + release helpers; centralize tool configs; set initial version 0.0.1\n\n- dev version current|bump <major|minor|patch> with CHANGELOG generation and annotated tags\n- dev release rc to create/push release-candidate\n- dev protect-main uses gh CLI to enable branch protection\n- Commitizen pre-commit commit-msg hook enforcing Conventional Commits\n- Configs in pyproject (ruff, mypy, pytest, commitizen)\n- Docs version set to 0.0.1 (6072fed)

### refactor
- modernize dev CLI and wire up uv entry point\n\n- Replace if-chain with match-case; add is_ci() and run_mypy_then()\n- Improve typing and docstrings; simplify ruff checks\n- Update wrapper entrypoints to call local main()\n- Add build-system (hatchling) and src/ layout packaging config\n- Configure [project.scripts] dev entry point; default dev dependency group via [tool.uv]\n- Add package __init__.py\n\nRun with: uv run dev --help (5875223)

### ci
- add GitHub Actions workflow; update pre-commit stages; make dev check treat no-tests (pytest rc=5) as success (9066908)

### chore
- centralize tool configs in pyproject (ruff, mypy, pytest); add return type to main() (65d5948)
- remove stale erasmus entrypoint and add pre-commit hook to run 'uv run dev check' (2963923)

### other
- Initial commit (fcbcabd)

## [0.0.1] - 2025-09-20

### feat
- semantic versioning + release helpers; centralize tool configs; set initial version 0.0.1\n\n- dev version current|bump <major|minor|patch> with CHANGELOG generation and annotated tags\n- dev release rc to create/push release-candidate\n- dev protect-main uses gh CLI to enable branch protection\n- Commitizen pre-commit commit-msg hook enforcing Conventional Commits\n- Configs in pyproject (ruff, mypy, pytest, commitizen)\n- Docs version set to 0.0.1 (6072fed)

### refactor
- modernize dev CLI and wire up uv entry point\n\n- Replace if-chain with match-case; add is_ci() and run_mypy_then()\n- Improve typing and docstrings; simplify ruff checks\n- Update wrapper entrypoints to call local main()\n- Add build-system (hatchling) and src/ layout packaging config\n- Configure [project.scripts] dev entry point; default dev dependency group via [tool.uv]\n- Add package __init__.py\n\nRun with: uv run dev --help (5875223)

### ci
- add GitHub Actions workflow; update pre-commit stages; make dev check treat no-tests (pytest rc=5) as success (9066908)

### chore
- centralize tool configs in pyproject (ruff, mypy, pytest); add return type to main() (65d5948)
- remove stale erasmus entrypoint and add pre-commit hook to run 'uv run dev check' (2963923)

### other
- Initial commit (fcbcabd)



