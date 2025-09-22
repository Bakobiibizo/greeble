# Dropdown Menu

- Purpose: Button-triggered menu with keyboard nav.
- Inputs: Menu items; selection callbacks.
- Endpoints: None required; static or server-rendered.
- Events: `greeble:menu:select`.
- Accessibility: role=menu; roving tabindex; arrow keys.
- States: Open/closed; disabled items.
- Theming hooks: Menu container, items.

## Copy & Paste Usage

Basic no-JS toggle using `<details>/<summary>`:

```html
<details class="greeble-dropdown">
  <summary class="greeble-button" aria-haspopup="menu">Menu</summary>
  <div role="menu" class="greeble-dropdown__menu">
    <a href="#" role="menuitem">Action</a>
    <a href="#" role="menuitem">Another action</a>
  </div>
</details>
```

You may emit a custom event (via `HX-Trigger` headers) like `{"greeble:menu:select": {"id": 1}}` in response to a selection if the menu items are HTMX links.
