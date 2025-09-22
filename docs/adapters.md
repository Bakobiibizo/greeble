# Framework Adapters

Greeble components are backend-agnostic, but the library includes helpers and patterns for the most
common Python frameworks. Use the CLI to scaffold templates and static assets, then wire endpoints as
shown below.

## FastAPI

```bash
uv run greeble add modal
uv run greeble add table
```

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from greeble.adapters.fastapi import template_response

app = FastAPI()
templates = Jinja2Templates("templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("greeble/modal.html", {"request": request})

@app.get("/modal/example")
async def modal_example(request: Request) -> HTMLResponse:
    return template_response(
        templates,
        template_name="greeble/modal.html",
        context={"request": request},
        request=request,
        partial_template="greeble/modal.partial.html",
    )
```

## Django

```bash
uv run greeble add table --project ./django_project
```

Add `templates/greeble/table.html` to your Django project, then reference it from a view:

```python
from django.shortcuts import render


def inventory_view(request):
    return render(request, "greeble/table.html", {})
```

Use Django template tags or views to serve HTMX partials defined in the component docs (e.g.,
`greeble/table.partial.html`).

## Flask

```bash
uv run greeble add drawer --project ./flask_app
```

```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("greeble/drawer.html")
```

Implement the HTMX endpoints (e.g., `/drawer/open`) to return partial templates. Combine with
`greeble.adapters.flask` helpers once implemented.
