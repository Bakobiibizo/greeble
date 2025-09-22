# Documentation Site

The docs site packages the component catalogue, usage guides, and live HTMX examples.

## Goals

- Render each component in a realistic flow with side-by-side HTML snippets.
- Surface framework-specific guidance (FastAPI, Django, Flask) next to each example.
- Provide accessibility checklists and testing notes so teams can copy confidently.
- Offer “Copy snippet” affordances that map directly to the files in
  `packages/greeble_components/components/`.

## Local preview

Until the static site generator is wired up, you can explore the components through the FastAPI
landing demo:

```bash
uv run python examples/site/landing.py
```

This demo imports the latest component templates and mirrors the behaviours described in the
individual component docs. Once the docs site is scaffolded (MkDocs or another SSG), copy the demo
snippets into Markdown pages to keep everything in sync. The [CLI guide](../cli.md) covers how to
pull components into your own projects.
