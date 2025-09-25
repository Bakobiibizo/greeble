# Component Catalogue

Every component ships with:

- Copy-and-paste HTML and HTMX attributes in `packages/greeble_components/components/<name>/templates/`
- Optional CSS in `static/<name>.css`
- This documentation describing purpose, server endpoints, accessibility, and theming hooks

Use the table below to jump to individual component notes.

| Component | Summary | Key Server Endpoints | Docs |
| --- | --- | --- | --- |
| Button | Primary, secondary, ghost, destructive, icon, and loading actions | — | [button.md](button.md) |
| Input | Text, email, select, textarea with validation swaps | `POST /input/validate` (example) | [input.md](input.md) |
| Modal | Dialog partial + trigger, focus, and form handling | `GET /modal/example`, `GET /modal/close`, `POST /modal/submit` | [modal.md](modal.md) |
| Toast | Global toast root and dismissible toast items | Any endpoint returning out-of-band fragments, `GET /toast/dismiss` | [toast.md](toast.md) |
| Table | Sortable/searchable account table with row actions | `GET /table`, `POST /table/search`, `POST /table/export`, `GET/POST/DELETE /table/accounts/...` | [table.md](table.md) |
| Drawer | Edge drawer trigger and partial | `GET /drawer/open`, `GET /drawer/close` | [drawer.md](drawer.md) |
| Dropdown | Native `<details>` dropdown menu | — | [dropdown.md](dropdown.md) |
| Tabs | Roving tab controls backed by HTMX partials | `GET /tabs/{tabKey}` | [tabs.md](tabs.md) |
| Stepper | Multi-step navigation scaffold | `GET /stepper/{stepKey}`, `POST /stepper/{stepKey}` | [stepper.md](stepper.md) |
| Palette | Command palette with search + selection | `POST /palette/search`, `POST /palette/select` | [palette.md](palette.md) |
| Infinite List | Sentinel-triggered lazy loading list | `GET /list` | [infinite-list.md](infinite-list.md) |
| Form (validated) | Server-validated form group | `POST /form/validate`, `POST /form/submit` | [form.md](form.md) |

### Using the docs

Each page follows a consistent structure:

- **Purpose** – the problem the component solves
- **Structure & Inputs** – markup expectations, data attributes, and ARIA usage
- **Server contract** – routes and behaviours required to make the component interactive
- **Events** – HX-Trigger payloads that the component emits or listens for
- **Accessibility** – keyboard/focus guidance and screen reader expectations
- **Theming** – CSS custom properties and classes you can override

When you copy markup into your project, update the endpoint URLs to match your routes and ensure
you return the documented fragments. The [landing demo](../site/index.md) contains practical
implementations that mirror the guidance here. To copy files directly, run
`uv run greeble add <component>`.
