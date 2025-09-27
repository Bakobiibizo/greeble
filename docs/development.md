---
description: RC-centered development workflow using dev CLI and template tools
auto_execution_mode: 3
---

# Development Workflow

This workflow documents the recommended day-to-day development process using the `dev` CLI, centered on `release-candidate`, along with optional template tooling.

## 0) Prerequisites
- Python 3.12+
- `uv` package manager
- `pre-commit`
- Optional: GitHub CLI `gh` (for branch protection and PR helpers)

## 1) Project setup
- Clone the repo and install hooks
```bash
git clone https://github.com/bakobiibizo/greeble
cd greeble
pre-commit install
```
- (Optional) Authenticate `gh`
```bash
gh auth login
```

## 2) Create a feature branch from `release-candidate`
- Use the CLI to create a branch from RC:
```bash
uv run dev branch-create feat/<short-topic>
# or interactively (will prompt):
uv run dev branch-create
```

## 3) Develop and validate locally
- Lint/format/type-check/test in one:
```bash
uv run dev check
```
- Or run tasks individually:
```bash
uv run dev lint
uv run dev format
uv run dev typecheck
uv run dev test
```
- Commit using Conventional Commits (enforced by commit-msg hook):
```bash
git commit -m "feat(scope): concise subject"
```

## 4) Keep your branch current
- Rebase your feature branch on the latest `release-candidate`:
```bash
uv run dev branch-rebase
# If push is rejected after rebase, follow with:
# git push --force-with-lease
```

## 5) Finalize your branch into `release-candidate`
- Merge the current branch into RC (no-fast-forward) and push RC:
```bash
uv run dev branch-finalize
```

## 6) Open PR from RC to main
- Create the PR using the latest `CHANGELOG.md` section as body:
```bash
uv run dev release-pr
```
- Merge policy: main can be configured to require 0 approvals if you’re solo, or 1+ approvals for teams (see step 8).

## 7) Cut a release (after RC → main is merged)
- On `main`, bump SemVer and tag with changelog generation:
```bash
uv run dev version bump <patch|minor|major>
# Then push commit and tag:
git push && git push --tags
```

## Notes
- Keep everyday work on feature branches off `release-candidate` so stacked features remain available.
- Use `uv run dev branch-rebase` regularly to reduce merge pain.
- Use `uv run dev check` before committing to catch issues early.