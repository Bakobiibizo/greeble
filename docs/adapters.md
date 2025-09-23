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

Use helpers from `greeble.adapters.django` to detect HTMX and render partials conditionally:

```python
from django.http import HttpRequest, HttpResponse
from greeble.adapters import django as g_django

def table(request: HttpRequest) -> HttpResponse:
    context = {"rows": [...]}
    return g_django.template_response(
        template_name="greeble/table.html",
        partial_template="greeble/table.partial.html",
        context=context,
        request=request,
        triggers={"greeble:table:update": {"page": 1}},
    )
```

Load the template tags and add CSRF to HTMX requests via `hx-headers`:

```django
{% load greeble_tags %}

<form
  hx-post="/form/submit"
  hx-headers='{% greeble_csrf_headers %}'
  hx-target="#form-status" hx-swap="innerHTML">
  ...
</form>
```

Django settings configuration:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "greeble.adapters",   # enables `{% load greeble_tags %}`
]

MIDDLEWARE = [
    # ...
    "django.contrib.messages.middleware.MessageMiddleware",
    "greeble.adapters.middleware.GreebleMessagesToToastsMiddleware",
]
```

Client toast listener (minimal example):

```html
<script>
  (function () {
    function renderToast(t) {
      var root = document.getElementById("greeble-toasts");
      if (!root) return;
      var el = document.createElement("div");
      el.className = "greeble-toast greeble-toast--" + (t.level || "info");
      el.setAttribute("role", "status");
      var body = document.createElement("div");
      body.className = "greeble-toast__body";
      var title = document.createElement("p");
      title.className = "greeble-toast__title";
      title.textContent = t.title || "";
      var msg = document.createElement("p");
      msg.className = "greeble-toast__message";
      msg.textContent = t.message || "";
      body.appendChild(title);
      body.appendChild(msg);
      var btn = document.createElement("button");
      btn.className = "greeble-toast__dismiss";
      btn.setAttribute("aria-label", "Dismiss");
      btn.textContent = "×";
      btn.addEventListener("click", function () { el.remove(); });
      el.appendChild(body);
      el.appendChild(btn);
      root.appendChild(el);
      setTimeout(function () { el.remove(); }, 5000);
    }
    document.addEventListener("greeble:toast", function (e) {
      var d = e.detail;
      if (Array.isArray(d)) d.forEach(renderToast); else if (d) renderToast(d);
    });
  })();
  </script>
```

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

Use helpers from `greeble.adapters.flask` to detect HTMX and render fragments:

```python
from flask import Flask, request
from greeble.adapters import flask as g_flask

app = Flask(__name__)

@app.get("/drawer/open")
def drawer_open():
    return g_flask.template_response(
        template_name="greeble/drawer.html",
        partial_template="greeble/drawer.partial.html",
        context={},
        request=request,
        triggers={"greeble:drawer:open": True},
    )
```
