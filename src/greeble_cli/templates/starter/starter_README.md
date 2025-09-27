# Greeble Starter

This project was scaffolded by the `greeble` CLI. It includes FastAPI routes and templates for all
v0.1 components so you can explore HTMX flows end-to-end.

## Getting started

```bash
# Option A: console script
uv run greeble-starter

# Option B: module invocation
uv run python -m greeble_starter
```

Open http://127.0.0.1:8050/ to view the landing page.

## Structure

- `src/greeble_starter/app.py` – FastAPI application exposing modal, drawer, table, palette, tabs,
  form, stepper, and infinite list endpoints
- `templates/` – Base layout (`index.html`) and component templates copied from Greeble
- `static/` – Core tokens (`greeble-core.css` copied via CLI) and a small site stylesheet

## Configure links

The landing page shows three buttons: Docs, GitHub, and Demo. You can change their targets with environment variables (read at runtime):

```bash
export GREEBLE_DOCS_URL="https://greeble-synai.ngrok.dev/docs"
export GITHUB_REPO_URL="https://github.com/bakobiibizo/greeble"
export GREEBLE_DEMO_URL="https://github.com/bakobiibizo/greeble/tree/release-candidate/examples"
uv run greeble-starter --port 8050
```

This starter intentionally keeps endpoints minimal. Explore full component flows in the repository `examples/` if you need richer demos.

## Next steps

1. Replace the placeholder data and copy with your own product language.
2. Remove components you do not need by deleting their templates/static files and endpoints.
3. Configure deployment with `uvicorn`/`hypercorn` or your preferred ASGI server.

For more details, see the [Greeble repository](https://github.com/bakobiibizo/greeble).
