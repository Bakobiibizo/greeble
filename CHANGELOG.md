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



