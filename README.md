# Greeble

Greeble is an HTML-first component library for server-rendered Python apps. Each component ships
with copy-and-paste markup, HTMX attributes, and CSS tokens so teams can build rich flows without a
JavaScript bundler.

## Highlights

- **HTML first:** Render everything on the server, enhance with HTMX or hyperscript when needed.
- **Accessible by default:** Components document roles, focus management, keyboard interaction, and
  ARIA contracts.
- **Framework friendly:** Works with Django, FastAPI, and Flask. Adapters expose helpers for
  partial rendering, HX headers, and CSRF handling.
- **Own the source:** The library copies snippets into your codebase so you can customise freely.
- **Design tokens included:** `greeble_core` provides colour, spacing, and typography tokens plus
  utilitarian CSS helpers.

## Quick start

1. **Install the package** (PyPI release coming soon). Until then, install from the repo:

   ```bash
   pip install git+https://github.com/bakobiibizo/greeble.git
   # or locally
   pip install -e .
   ```

2. **Include the core CSS tokens** in your base template. The tokens live at
   `packages/greeble_core/assets/css/greeble-core.css`:

   ```html
   <link rel="stylesheet" href="/static/greeble/greeble-core.css" />
   ```

3. **Drop in component markup.** Every component directory under
   `packages/greeble_components/components/<name>/templates/` contains trigger markup and partials.
   Copy them into your templates or render them directly.

4. **Wire server endpoints.** Components document the routes they expect. With FastAPI you can use
   the bundled adapter to serve full layouts or partial fragments:

   ```python
   from fastapi import FastAPI, Request
   from fastapi.templating import Jinja2Templates
   from greeble.adapters.fastapi import template_response

   app = FastAPI()
   templates = Jinja2Templates("templates")

   @app.get("/modal/example")
   async def modal_example(request: Request):
       return template_response(
           templates,
           "modal.html",
           context={},
           request=request,
           partial_template="modal.partial.html",
       )
   ```

5. **Return out-of-band updates when needed.** Toasts and other shared UI ship with helper partials
   that set `hx-swap-oob="true"` so a single response can update multiple regions.

See the [component docs](docs/components/README.md) for contract details, events, and accessibility
notes for each snippet.

## CLI

Use the bundled CLI to copy component files into your project:

```bash
uv run greeble list                      # view available components
uv run greeble add modal                 # copy modal templates/CSS into ./templates and ./static
uv run greeble add table --project ./apps/main --include-docs
uv run greeble sync modal                # re-copy modal, overwriting local edits
uv run greeble remove table              # remove previously copied files
uv run greeble doctor --project ./apps/main  # sanity check manifest + project dirs
```

Common options:

- `--project` – destination root (default: current directory)
- `--templates` / `--static` – customise template/static roots (defaults: `templates`, `static`)
- `--include-docs` – copy or remove the component documentation page alongside markup/CSS
- `--force` – overwrite existing files during `add`
- `--dry-run` – preview copy/removal plans without writing

See [docs/cli.md](docs/cli.md) for a full walkthrough.

## Live examples

Spin up the landing demo to explore the full component slice:

```bash
uv run python examples/site/landing.py
```

The demo mounts the core CSS, imports the latest component templates, and exposes HTMX endpoints
for modals, drawers, tab content, table pagination, infinite lists, and toast queues.

## Component catalog

| Component | Summary | Docs |
| --- | --- | --- |
| Buttons | Primary, secondary, ghost, destructive, icon, loading variations | [docs/components/button.md](docs/components/button.md) |
| Inputs | Text, email, select, textarea patterns with validation flow | [docs/components/input.md](docs/components/input.md) |
| Modal | Dialog partial with backdrop, focus management, form example | [docs/components/modal.md](docs/components/modal.md) |
| Toasts | Out-of-band toast root and item fragments for global feedback | [docs/components/toast.md](docs/components/toast.md) |
| Table | Sortable, searchable table shell with server actions | [docs/components/table.md](docs/components/table.md) |
| Drawer, Dropdown, Tabs, Stepper, Palette, Infinite List | See individual docs in `docs/components/` | — |

## Framework helpers

- `greeble.adapters.fastapi` – HTMX-aware helpers for partial detection, HX trigger headers, and
  template rendering.
- Placeholders exist for Django and Flask adapters; contributions are welcome to bring those to
  parity with the FastAPI implementation.
- See [docs/adapters.md](docs/adapters.md) for quick-start patterns with the CLI.

## Repository layout

```
packages/
  greeble_core/                 # Shared CSS tokens and utilities
  greeble_components/           # Component markup, CSS, and docs
  adapters/                     # Framework-specific helpers
examples/                       # Demo apps (FastAPI, Django, Flask) and landing flow
src/greeble/                    # Installable Python package surface
```

## Contributing

1. Fork the repo and create a branch.
2. Run the demo and tests locally: `uv run dev test`.
3. Format and lint: `uv run dev check`.
4. Submit a pull request that includes documentation updates for new components or behaviours.

## License

MIT License © 2025 Greeble contributors.
