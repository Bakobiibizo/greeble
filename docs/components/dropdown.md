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
