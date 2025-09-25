# Dropdown Menu

- Purpose: Button-triggered action menu for contextual commands.
- Structure: `<details class="greeble-dropdown">` with a summary button and a panel containing
  `role="menuitem"` buttons/links.
- Endpoints: Optional HTMX actions such as `GET /workspace/settings` or `POST /workspace/invite`.
- Events: Emit `HX-Trigger: {"greeble:menu:select": {"action": "invite"}}` from the server when an
  item completes.
- Accessibility: Summary exposes `aria-haspopup="menu"`; the panel is `role="menu"`.
- Theming hooks: `.greeble-dropdown__panel`, `.greeble-dropdown__item`, `.greeble-dropdown__chevron`,
  and `.greeble-dropdown__item-kbd` can all be themed via CSS or tokens.

## Copy & Paste

```html
<details class="greeble-dropdown" data-dropdown>
  <summary class="greeble-dropdown__button" aria-haspopup="menu">
    Workspace actions
    <span class="greeble-dropdown__chevron" aria-hidden="true">▾</span>
  </summary>
  <div class="greeble-dropdown__panel" role="menu" aria-label="Workspace actions">
    <button class="greeble-dropdown__item" type="button" role="menuitem"
            hx-get="/workspace/settings" hx-target="#workspace-panel" hx-swap="innerHTML">
      <span class="greeble-dropdown__item-label">Open settings</span>
      <span class="greeble-dropdown__item-kbd">⌘ ,</span>
    </button>
    <button class="greeble-dropdown__item" type="button" role="menuitem"
            hx-post="/workspace/invite" hx-target="#invite-root" hx-swap="innerHTML">
      <span class="greeble-dropdown__item-label">Invite teammate</span>
      <span class="greeble-dropdown__item-hint">Sends a magic link</span>
    </button>
    <a class="greeble-dropdown__item" role="menuitem" href="/billing" data-navigation="true">
      <span class="greeble-dropdown__item-label">View billing</span>
      <span class="greeble-dropdown__item-kbd">⌘ B</span>
    </a>
  </div>
</details>
```

Ensure server responses either navigate (for anchor items) or return fragments/toasts when using HTMX
menu items.

## Keyboard map

- Enter / Space – Toggle `<details>` open/closed from the summary button; activate focused menu item.
- Esc – Close the menu when open.
- Arrow Up/Down – Move focus between menu items (client JS optional; native tab order is acceptable).
- Tab / Shift+Tab – Move between focusable elements; keep focus within the panel while open.

## Response matrix

- GET /workspace/settings (example)
  - 200 OK — returns fragment for the target region (`hx-target`)
  - Headers: optional `HX-Trigger: {"greeble:menu:select": {"action": "settings"}}`

- POST /workspace/invite (example)
  - 200 OK — returns out-of-band toast and/or inline confirmation
  - 422/400 — return inline error fragment in panel or toast with guidance

- Link navigation items (`<a href="…" data-navigation="true">`)
  - Standard navigation; no fragment expected. Server may still emit `HX-Trigger` via redirects.

## View source

- Template: [dropdown.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/dropdown/templates/dropdown.html)
- Styles: [dropdown.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/dropdown/static/dropdown.css)
