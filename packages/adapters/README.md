# Adapters

This directory contains Python framework adapters for using Greeble with common server frameworks.

- `greeble_fastapi`: Helpers for HTMX-aware partial rendering and HX-Trigger headers.
- `greeble_flask`: Helpers for HTMX detection, partial rendering via Jinja, and HX-Trigger headers.
- `greeble_django`: Template tags (`{% greeble_toast_container %}`, `{% greeble_csrf_headers %}`), CSRF helpers, and a messages-to-toasts middleware.

See the library docs for usage and examples: `docs/adapters.md`. Minimal demo apps live in:

- `examples/django-demo/`
- `examples/flask-demo/`
