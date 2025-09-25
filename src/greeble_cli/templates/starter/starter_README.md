# Greeble Starter

This project was scaffolded by the `greeble` CLI. It includes FastAPI routes and templates for all
v0.1 components so you can explore HTMX flows end-to-end.

## Getting started

```bash
uv run uvicorn greeble_starter.app:app --reload
```

Open http://127.0.0.1:8050/ to interact with the demo endpoints.

## Structure

- `src/greeble_starter/app.py` – FastAPI application exposing modal, drawer, table, palette, tabs,
  form, stepper, and infinite list endpoints
- `templates/` – Base layout (`index.html`) and component templates copied from Greeble
- `static/` – Core tokens (`greeble-core.css` copied via CLI) and a small site stylesheet

## Next steps

1. Replace the placeholder data and copy with your own product language.
2. Remove components you do not need by deleting their templates/static files and endpoints.
3. Configure deployment with `uvicorn`/`hypercorn` or your preferred ASGI server.

For more details, see the [Greeble repository](https://github.com/bakobiibizo/greeble).
