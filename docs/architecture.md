# Greeble: Architecture and Design Document

**Version:** 0.0.1
**Audience:** Python-first web developers building server-rendered interfaces with HTMX
**Authoring mode:** HTML-first, progressive enhancement, copy and paste components

---

## 1. Purpose

Greeble is an HTML-first component library that delivers copy and paste snippets powered by HTMX for rapid UI construction. The library targets Python frameworks first (Django, FastAPI, Flask), while remaining backend agnostic. The goal is to provide a set of accessible, unopinionated building blocks that work without a JavaScript bundler, can be themed with design tokens, and define predictable server contracts.

## 2. Goals

1. Copy and paste components that work out of the box with HTMX, no bundler required.
2. First-class documentation and adapters for Django, FastAPI, and Flask.
3. Accessible by default, including keyboard flows, focus management, and ARIA roles.
4. Theming through CSS variables and an optional Tailwind preset. No lock-in.
5. Predictable server contracts: each component declares expected endpoints, inputs, events, and return shapes.
6. Ownership of source: the CLI copies files into the application so teams can modify freely.

## 3. Non-Goals

1. A full reactive component framework. Greeble enhances server-rendered HTML instead of replacing it.
2. Shipping a runtime JavaScript framework. The baseline is HTMX and optional Hyperscript.
3. Locking teams into a specific CSS utility framework. Tailwind support is an add-on.

## 4. Core Principles

* **HTML first:** render everything on the server, apply interactivity through HTMX attributes.
* **Progressive enhancement:** components function without client scripting, then enhance behavior when HTMX is present.
* **Accessibility by default:** roles, names, focus management, and keyboard interaction are designed in from the start.
* **Stable contracts:** the markup API and server contract are explicit and versioned.
* **Learn by viewing source:** every example page exposes the exact HTML that gets pasted.

---

## 5. High-Level Architecture

### 5.1 Package Layout

```
greeble/
  packages/
    greeble-core/                # CSS tokens, resets, low-level utilities
    greeble-components/          # Copy and paste HTML snippets with HTMX attributes
    greeble-hyperscript/         # Optional interactions as <script type="text/hyperscript">
    greeble-tailwind-preset/     # Optional Tailwind preset mapped to CSS variables
    adapters/
      greeble-django/            # Template tags, CSRF helpers, messages-to-toasts, pagination helpers
      greeble-fastapi/           # Template utilities, partial helpers, HX-Trigger helpers
      greeble-flask/             # Blueprint with helpers matching the FastAPI adapter
  tools/
    greeble-cli/                 # `greeble add <component>` copies component files into the app
  docs/
    site/                        # Documentation site with live examples and source view
  examples/
    fastapi-demo/
    django-demo/
    flask-demo/
```

### 5.2 Runtime Overview

* Components are HTML fragments with HTMX attributes and CSS classes.
* The server returns partial templates that replace targets or apply out of band swaps.
* Optional Hyperscript snippets handle focus, keyboard navigation, and small behaviors without a bundler.
* The adapters provide ergonomics for CSRF, flash messages, and HTMX-aware rendering.

### 5.3 Data Flow

1. A user action triggers an HTMX request via `hx-get` or `hx-post`.
2. The server endpoint validates input, executes domain logic, and returns an HTML fragment.
3. HTMX swaps the fragment into the target element. Optional out of band fragments update shared zones such as a toast container.
4. Optional custom events inform other components about state changes.

---

## 6. Styling and Theming

### 6.1 Design Tokens

A small set of CSS variables controls colors, spacing, radii, shadows, and transitions. These are defined in `greeble-core` and can be overridden on `:root` or on a theme scope.

```css
:root {
  --greeble-color-background: #0b0b0c;
  --greeble-color-foreground: #e8e8ea;
  --greeble-color-muted: #a0a0a7;
  --greeble-color-accent: #6aa1ff;
  --greeble-radius-medium: 12px;
  --greeble-shadow-1: 0 1px 2px rgba(0,0,0,.2);
  --greeble-shadow-2: 0 8px 30px rgba(0,0,0,.35);
  --greeble-spacing-1: .25rem;
  --greeble-spacing-2: .5rem;
  --greeble-spacing-3: .75rem;
  --greeble-spacing-4: 1rem;
  --greeble-focus-ring: 0 0 0 3px rgba(106,161,255,.5);
}
```

### 6.2 Utility Classes

`greeble-core` includes a light utility sheet for common layout patterns: stack, cluster, grid, visually hidden, and focus ring helpers. Teams can keep these or replace them.

### 6.3 Tailwind Preset

`greeble-tailwind-preset` maps the CSS variables to Tailwind theme tokens. Teams using Tailwind can opt in without rewriting components.

---

## 7. Component Specification Format

Each component ships with:

* `component.html` (trigger markup that lives in your page)
* `component.partial.html` (server-rendered fragment that gets returned by endpoints)
* `component.hyperscript.html` (optional behavior)
* `README.md` (contract and accessibility guidance)

Each component must document:

* **Inputs:** data attributes, form fields, and ARIA attributes.
* **Endpoints:** routes, HTTP methods, expected parameters, and return fragments.
* **Events:** custom events emitted or consumed.
* **Accessibility:** roles, names, keyboard interactions, and focus management.
* **States:** loading, error, empty, and success visuals.
* **Theming hooks:** tokens and classes involved.

### 7.1 Example: Modal Component

**Trigger Markup**

```html
<button
  class="greeble-button"
  hx-get="/modal/example"
  hx-target="#modal-root"
  hx-trigger="click"
  hx-swap="innerHTML">
  Open Modal
</button>

<div id="modal-root" aria-live="polite"></div>
```

**Returned Partial**

```html
<div
  id="greeble-modal"
  role="dialog"
  aria-modal="true"
  aria-labelledby="greeble-modal-title"
  class="greeble-modal"
  _="on load call #greeble-modal.focus()">
  <div class="greeble-modal__backdrop"
       hx-trigger="click"
       hx-get="/modal/close"
       hx-target="#modal-root"
       hx-swap="innerHTML"></div>

  <div class="greeble-modal__panel" tabindex="-1">
    <header class="greeble-modal__header">
      <h2 id="greeble-modal-title" class="greeble-heading-2">Example modal</h2>
      <button class="greeble-icon-button"
              aria-label="Close"
              hx-get="/modal/close"
              hx-target="#modal-root"
              hx-swap="innerHTML">×</button>
    </header>

    <div class="greeble-modal__body">
      <p>Content here</p>
      <form
        hx-post="/modal/submit"
        hx-target="#modal-root"
        hx-swap="innerHTML">
        <input name="email" type="email" required class="greeble-input" />
        <button class="greeble-button greeble-button--accent" type="submit">Submit</button>
      </form>
    </div>
  </div>
</div>
```

**Server Endpoints**

* `GET /modal/example` returns the modal partial
* `GET /modal/close` returns an empty string
* `POST /modal/submit` returns a success partial or validation errors

**Accessibility**

* Focus sent to the panel on open, Escape closes via a visible close button or an optional key handler in Hyperscript.
* Backdrop has a descriptive label on the dialog container, not on the backdrop itself.

---

## 8. Python Adapters

### 8.1 Django Adapter

* Template tag `{% greeble_toast_container %}` injects a single toast root.
* Template tag `{% greeble_csrf_headers %}` prints `hx-headers` for CSRF.
* Middleware converts `django.contrib.messages` into out of band toast fragments.
* Pagination helper generates `hx-get` links targeting a table body.

### 8.2 FastAPI Adapter

* `HTMXPartial` response helper for fragments, with optional event triggers via `HX-Trigger` headers.
* Jinja2 template utilities for deciding layout versus partial based on the `HX-Request` header.

### 8.3 Flask Adapter

* Blueprint with helpers matching FastAPI semantics.

---

## 9. CLI

### 9.1 Purpose

The CLI copies component files into the application, initializes tokens and utilities, and optionally installs a Tailwind preset.

### 9.2 Commands

```
greeble add <component-name>
greeble add table --features pagination,sorting
greeble theme init --preset minimal
greeble doctor
```

### 9.3 Behavior

* Verifies destination paths and writes files under `templates/greeble` and `static/greeble` by default.
* Never hides files. The application owns and edits all copied files.
* Prints follow-up instructions for wiring endpoints and optional adapter helpers.

---

## 10. Events and Swap Conventions

* Loading indicators: use `hx-indicator=".greeble-loading"` on a component root that contains a spinner element.
* Error handling: fragments can mark error roots with `data-greeble-error="true"` so styles can switch to an error state.
* Out of band zones: `#greeble-toasts` for toasts, `#greeble-dialog-root` for modals, `#greeble-announcer` for live regions.
* Custom events: components may emit `greeble:success`, `greeble:error`, or more specific events.

---

## 11. Accessibility Requirements

* All interactive elements are keyboard reachable and operable.
* Dialogs manage focus and restore focus to the trigger on close.
* Menus and lists use roving tabindex when appropriate.
* All form controls have programmatic names and visible labels.
* Announce dynamic updates through `aria-live` regions when content changes non-modally.

---

## 12. Security Considerations

* CSRF documentation per framework, plus helpers for headers on HTMX requests.
* Validation on server endpoints for state-changing requests, even when triggered by HTMX.
* Rate limits for high-frequency triggers, such as typeahead and command palette.
* Clear guidance on safely rendering untrusted content in fragments.

---

## 13. Versioning and Stability

* Semantic versioning for all packages.
* `greeble-components` treats any change to HTML structure, required attributes, or data attributes as a breaking change that bumps the major version.
* Adapters maintain minor version compatibility within a major series.

---

## 14. Testing and Quality

* Example servers in `examples/` for FastAPI, Django, and Flask, each rendering every component.
* Playwright-based snapshot tests for visual regressions.
* `axe-core` automated accessibility checks on example pages.
* Contract tests that render fragments with sample context to validate required fields and states.

---

## 15. Initial Component Catalog

Each entry includes a summary, expected endpoints, events, and accessibility notes. The manifest below encodes these details for scaffolding.

### 15.1 Buttons

* **Summary:** Primary, secondary, icon, and split buttons.
* **Endpoints:** None, buttons act as triggers.
* **Events:** Emit `greeble:click` as an optional custom event.
* **Accessibility:** Visible focus, `aria-pressed` for toggle variants.

### 15.2 Inputs

* **Summary:** Text input, textarea, select, and a combobox pattern.
* **Endpoints:** Validation endpoint optional.
* **Events:** `greeble:validate` optional.
* **Accessibility:** Labeled controls, `aria-describedby` for help text and errors.

### 15.3 Modal

* **Summary:** Dialog with focus trap, backdrop, and close controls.
* **Endpoints:** `GET /modal/example`, `GET /modal/close`, `POST /modal/submit`.
* **Events:** `greeble:modal:open`, `greeble:modal:close`.
* **Accessibility:** `role="dialog"`, `aria-modal="true"`, managed focus.

### 15.4 Drawer

* **Summary:** Edge panel for settings and filters.
* **Endpoints:** Open, close, and optional save.
* **Events:** `greeble:drawer:open`, `greeble:drawer:close`.
* **Accessibility:** `role="dialog"` with labeled header.

### 15.5 Dropdown Menu

* **Summary:** Button-triggered menu with keyboard navigation.
* **Endpoints:** None required, content is server-rendered or static.
* **Events:** `greeble:menu:select`.
* **Accessibility:** `role="menu"`, roving tabindex, arrow key navigation.

### 15.6 Tabs

* **Summary:** Tablist with per-tab content via `hx-get`.
* **Endpoints:** `GET /tabs/<tab>`.
* **Events:** `greeble:tab:change`.
* **Accessibility:** `role="tablist"`, `role="tab"`, `aria-controls`, and `aria-selected`.

### 15.7 Table

* **Summary:** Sortable, pageable table with row actions.
* **Endpoints:** `GET /table?page=<n>&sort=<field>:<dir>`.
* **Events:** `greeble:table:sorted`, `greeble:table:paged`.
* **Accessibility:** Proper table semantics, captions, and summaries.

### 15.8 Toasts

* **Summary:** Global toast queue using out of band swaps.
* **Endpoints:** Any server event can return out of band toast fragments.
* **Events:** `greeble:toast`.
* **Accessibility:** `aria-live="assertive"` with timeouts announced.

### 15.9 Command Palette

* **Summary:** Input with server-backed results and keyboard selection.
* **Endpoints:** `POST /palette/search`.
* **Events:** `greeble:palette:select`.
* **Accessibility:** `role="dialog"` with listbox semantics for results.

### 15.10 Stepper

* **Summary:** Multi-step wizard with back and next actions.
* **Endpoints:** `GET /stepper/<step>`, `POST /stepper/<step>`.
* **Events:** `greeble:stepper:change`.
* **Accessibility:** Announce step changes and disabled states.

### 15.11 Infinite List

* **Summary:** Lazy loading list using `hx-trigger="revealed"` on a sentinel.
* **Endpoints:** `GET /list?cursor=<id>`.
* **Events:** `greeble:list:append`.
* **Accessibility:** Maintain position, announce new content.

### 15.12 Form with Validation Pattern

* **Summary:** Server-validated form that replaces only invalid groups.
* **Endpoints:** `POST /form/validate`, `POST /form/submit`.
* **Events:** `greeble:form:invalid`, `greeble:form:submitted`.
* **Accessibility:** Field-level error messages with `aria-describedby`.

---

## 16. Scaffolding Manifest

The manifest declares the component catalog, file outputs, and contracts. The CLI consumes this file to scaffold a project or add components.

```yaml
# greeble.manifest.yaml
version: 1
library:
  name: "Greeble"
  description: "HTML-first, HTMX-powered copy and paste components for Python-first apps"
  packages:
    - greeble-core
    - greeble-components
    - greeble-hyperscript
    - greeble-tailwind-preset
    - greeble-django
    - greeble-fastapi
    - greeble-flask
  tokens_file: "static/greeble/greeble-core.css"
  docs_site: "docs/site"

components:
  - key: button
    title: "Buttons"
    summary: "Primary, secondary, icon, and split buttons"
    files:
      - templates/greeble/button.html
      - static/greeble/button.css
      - docs/components/button.md
    endpoints: []
    events:
      emits: ["greeble:click"]
      listens: []
    accessibility:
      notes: ["Visible focus", "aria-pressed for toggle variants"]

  - key: input
    title: "Inputs"
    summary: "Text input, textarea, select, and combobox"
    files:
      - templates/greeble/input.html
      - static/greeble/input.css
      - docs/components/input.md
    endpoints:
      - method: POST
        path: "/input/validate"
        description: "Optional server validation for demo purposes"
    events:
      emits: ["greeble:validate"]
      listens: []
    accessibility:
      notes: ["Labels required", "aria-describedby for help and errors"]

  - key: modal
    title: "Modal"
    summary: "Dialog with focus trap and backdrop"
    files:
      - templates/greeble/modal.html
      - templates/greeble/modal.partial.html
      - templates/greeble/modal.hyperscript.html
      - static/greeble/modal.css
      - docs/components/modal.md
    endpoints:
      - method: GET
        path: "/modal/example"
        description: "Return the modal partial"
      - method: GET
        path: "/modal/close"
        description: "Close the modal by clearing the root"
      - method: POST
        path: "/modal/submit"
        description: "Handle form submit and return success or errors"
    events:
      emits: ["greeble:modal:open", "greeble:modal:close"]
      listens: []
    accessibility:
      notes: ["role=dialog with aria-modal", "focus sent to panel on open"]

  - key: drawer
    title: "Drawer"
    summary: "Edge panel for settings and filters"
    files:
      - templates/greeble/drawer.html
      - templates/greeble/drawer.partial.html
      - static/greeble/drawer.css
      - docs/components/drawer.md
    endpoints:
      - method: GET
        path: "/drawer/open"
      - method: GET
        path: "/drawer/close"
    events:
      emits: ["greeble:drawer:open", "greeble:drawer:close"]
      listens: []
    accessibility:
      notes: ["role=dialog", "label with heading"]

  - key: dropdown
    title: "Dropdown Menu"
    summary: "Button-triggered menu with keyboard navigation"
    files:
      - templates/greeble/dropdown.html
      - static/greeble/dropdown.css
      - docs/components/dropdown.md
    endpoints: []
    events:
      emits: ["greeble:menu:select"]
      listens: []
    accessibility:
      notes: ["role=menu with roving tabindex", "arrow key navigation"]

  - key: tabs
    title: "Tabs"
    summary: "Tablist with per-tab content"
    files:
      - templates/greeble/tabs.html
      - templates/greeble/tabs.partial.html
      - static/greeble/tabs.css
      - docs/components/tabs.md
    endpoints:
      - method: GET
        path: "/tabs/{tabKey}"
        description: "Return content for a given tab key"
    events:
      emits: ["greeble:tab:change"]
      listens: []
    accessibility:
      notes: ["role=tablist and role=tab", "aria-selected and aria-controls"]

  - key: table
    title: "Table"
    summary: "Sortable, pageable table with row actions"
    files:
      - templates/greeble/table.html
      - templates/greeble/table.partial.html
      - static/greeble/table.css
      - docs/components/table.md
    endpoints:
      - method: GET
        path: "/table"
        description: "Accepts page and sort query parameters"
    events:
      emits: ["greeble:table:sorted", "greeble:table:paged"]
      listens: []
    accessibility:
      notes: ["caption recommended", "scope attributes on headers"]

  - key: toast
    title: "Toasts"
    summary: "Global toast queue using out of band swaps"
    files:
      - templates/greeble/toast.root.html
      - templates/greeble/toast.item.html
      - static/greeble/toast.css
      - docs/components/toast.md
    endpoints: []
    events:
      emits: ["greeble:toast"]
      listens: []
    accessibility:
      notes: ["aria-live=assertive on root", "dismiss buttons with labels"]

  - key: palette
    title: "Command Palette"
    summary: "Search input with server-backed results"
    files:
      - templates/greeble/palette.html
      - templates/greeble/palette.partial.html
      - static/greeble/palette.css
      - docs/components/palette.md
    endpoints:
      - method: POST
        path: "/palette/search"
        description: "Return result list items"
    events:
      emits: ["greeble:palette:select"]
      listens: []
    accessibility:
      notes: ["role=dialog with listbox semantics", "announce result counts"]

  - key: stepper
    title: "Stepper"
    summary: "Multi-step wizard"
    files:
      - templates/greeble/stepper.html
      - templates/greeble/stepper.partial.html
      - static/greeble/stepper.css
      - docs/components/stepper.md
    endpoints:
      - method: GET
        path: "/stepper/{stepKey}"
      - method: POST
        path: "/stepper/{stepKey}"
    events:
      emits: ["greeble:stepper:change"]
      listens: []
    accessibility:
      notes: ["announce step changes", "disable next when invalid"]

  - key: infinite-list
    title: "Infinite List"
    summary: "Lazy loading list triggered on reveal"
    files:
      - templates/greeble/infinite-list.html
      - templates/greeble/infinite-list.partial.html
      - static/greeble/infinite-list.css
      - docs/components/infinite-list.md
    endpoints:
      - method: GET
        path: "/list"
        description: "Accepts cursor query parameter"
    events:
      emits: ["greeble:list:append"]
      listens: []
    accessibility:
      notes: ["maintain scroll position", "announce new content"]

  - key: form-validated
    title: "Form with Validation"
    summary: "Server-validated form that replaces invalid groups"
    files:
      - templates/greeble/form.html
      - templates/greeble/form.partial.html
      - static/greeble/form.css
      - docs/components/form.md
    endpoints:
      - method: POST
        path: "/form/validate"
      - method: POST
        path: "/form/submit"
    events:
      emits: ["greeble:form:invalid", "greeble:form:submitted"]
      listens: []
    accessibility:
      notes: ["associate errors with fields via aria-describedby"]
```

---

## 17. Documentation Site Plan

* Live examples for every component with a “View HTML” and “Copy” button.
* Side-by-side snippets for Django, FastAPI, and Flask endpoints.
* Patterns section: CRUD with HTMX, streaming updates, pagination and sorting, and validation flows.
* Accessibility checklists per component.

---

## 18. Roadmap

* 0.1: Buttons, Inputs, Modal, Toasts, Table, Dropdown Menu.
* 0.2: Tabs, Drawer, Stepper, Infinite List.
* 0.3: Command Palette, Combobox improvements, Tree View.
* 0.4: File Upload pattern, Data Grid enhancements, Date Picker.

---

## 19. Open Questions

* Should the library ship optional Alpine.js shims for teams who prefer it over Hyperscript, or should that remain an external recipe.
* How strict should the adapters be about differentiating HTMX requests from normal submits when deciding which template to render.
* What level of configurability is needed for keyboard bindings in the command palette and menu components.

---

## 20. Appendix: Minimal FastAPI Example

```python
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates("templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/modal/example", response_class=HTMLResponse)
def modal_example(request: Request):
    return templates.TemplateResponse("greeble/modal.partial.html", {"request": request})

@app.get("/modal/close", response_class=HTMLResponse)
def modal_close():
    return HTMLResponse("")

@app.post("/modal/submit", response_class=HTMLResponse)
def modal_submit(request: Request, email: str = Form(...)):
    html = f"""
    <div id=\"greeble-toasts\" hx-swap-oob=\"true\">
      <div class=\"greeble-toast greeble-toast--success\">Saved {email}</div>
    </div>
    """
    return HTMLResponse(html)
```

---

## 21. Appendix: Token Starter

```css
:root {
  --greeble-color-background: #0b0b0c;
  --greeble-color-foreground: #e8e8ea;
  --greeble-color-muted: #a0a0a7;
  --greeble-color-accent: #6aa1ff;
  --greeble-radius-medium: 12px;
  --greeble-shadow-1: 0 1px 2px rgba(0,0,0,.2);
  --greeble-shadow-2: 0 8px 30px rgba(0,0,0,.35);
  --greeble-spacing-1: .25rem;
  --greeble-spacing-2: .5rem;
  --greeble-spacing-3: .75rem;
  --greeble-spacing-4: 1rem;
  --greeble-focus-ring: 0 0 0 3px rgba(106,161,255,.5);
}

.greeble-button { padding: var(--greeble-spacing-2) var(--greeble-spacing-4); border-radius: var(--greeble-radius-medium); box-shadow: var(--greeble-shadow-1); }
.greeble-button--accent { background: var(--greeble-color-accent); color: #0b0b0c; }
.greeble-input { background: #151518; color: var(--greeble-color-foreground); border: 1px solid #2a2a32; padding: var(--greeble-spacing-2) var(--greeble-spacing-3); border-radius: 10px; }
.greeble-modal { position: fixed; inset: 0; display: grid; place-items: center; }
.greeble-modal__backdrop { position: absolute; inset: 0; background: rgba(0,0,0,.5); }
.greeble-modal__panel { position: relative; background: #101014; color: var(--greeble-color-foreground); border-radius: var(--greeble-radius-medium); padding: var(--greeble-spacing-4); box-shadow: var(--greeble-shadow-2); }
.greeble-icon-button:focus-visible { outline: none; box-shadow: var(--greeble-focus-ring); }
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
```
