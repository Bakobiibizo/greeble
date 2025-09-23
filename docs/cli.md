# Greeble CLI

The `greeble` command scaffolds starter projects and copies component templates, static assets, and
optional documentation into your project. The CLI reads `greeble.manifest.yaml`, so new components
added to the manifest are immediately available.

## Installation

The CLI is installed alongside the Python package. If you installed the project with `pip install -e .`
or from Git, run commands via `uv run` (or your chosen virtualenv):

```bash
uv run greeble list
```

## Commands

### `greeble list`

Lists all component keys, titles, and summaries.

### `greeble new <project>`

Scaffolds a FastAPI starter project seeded with Greeble components, endpoint skeletons, static
assets, and a README/pyproject configured for `uv`.

Options:

- `--include-docs` – copy component documentation pages into `<project>/docs`
- `--force` – overwrite any existing files in the destination
- `--dry-run` – preview the files that would be generated without writing

### `greeble add <component>`

Copies template and static files for a component into your project.

Options:

- `--project PATH` (default: current directory)
- `--templates PATH` (default: `templates`) – destination root for HTML templates
- `--static PATH` (default: `static`) – destination root for CSS/JS assets
- `--include-docs` – also copy the component documentation page
- `--force` – overwrite existing files
- `--dry-run` – preview without writing

### `greeble sync <component>`

Re-copies the component files, overwriting existing ones. Supports the same options as `add`
(excluding `--force`, which is implied).

### `greeble remove <component>`

Deletes files previously copied for a component. Accepts the same project/template/static/doc paths
as `add`. Use `--dry-run` to preview which files would be removed.

### `greeble doctor`

Validates the manifest and (optionally) a project directory. With `--project`, the command checks for
expected template/static directories and reports missing files.

## Example workflow

```bash
uv run greeble new ./apps/starter --include-docs
uv run greeble add modal --project ./apps/site --include-docs
uv run greeble add table --project ./apps/site
uv run greeble sync table --project ./apps/site          # overwrite local edits with upstream copy
uv run greeble remove modal --project ./apps/site        # remove modal files
uv run greeble doctor --project ./apps/site --include-docs
```

## Where files land

Given a component manifest entry such as `templates/greeble/modal.html`, `greeble add modal` writes to:

```
<project>/templates/greeble/modal.html
<project>/static/greeble/modal.css
```

Documentation files (when `--include-docs` is set) are copied verbatim relative to the project root,
e.g. `<project>/docs/components/modal.md`.

## Extending the manifest

Add new component entries to `greeble.manifest.yaml` with their template/static/doc paths. The CLI will
automatically surface them in `greeble list` and support `greeble add <new-component>`.
