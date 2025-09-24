## [0.1.1] - 2025-09-23

### refactor
- extract HTMX utils; preserve HX-Trigger toasts; tighten manifest library keys; demo parity + docs todos (b33e15b)

### chore
- remove partial_html from Django/Flask; enforce template-based rendering; update tests (541f996)
- changed demo to use env variables over hard coding debug=true (c465200)

## [0.1.0] - 2025-09-23

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



