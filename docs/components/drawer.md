# Drawer

- Purpose: Slide-in panel for contextual upgrades, filters, or settings.
- Structure: Trigger button mounts `#drawer-root`; partial returns a dialog with backdrop, header,
  stacked body content, and action footer.
- Endpoints: `GET /drawer/open` (returns partial), `GET /drawer/close` (clears root), optional
  `POST /drawer/subscribe` (form submission).
- Events: Emit `HX-Trigger: {"greeble:drawer:open": true}` when opening and
  `{"greeble:drawer:close": true}` when the user dismisses the panel. Toast submissions can emit
  `greeble:toast` payloads.
- Accessibility: Declares `role="dialog"`, `aria-modal="true"`, labelled heading/description, and
  focuses the panel via `tabindex="-1"`. Backdrop button provides an `aria-label` for screen
  readers.
- Theming hooks: `.greeble-drawer__panel`, `.greeble-drawer__eyebrow`, `.greeble-drawer__actions`,
  and `.greeble-drawer__list` expose distinct styling knobs. All spacing pulls from
  `greeble_core` tokens.

## Copy & Paste

## Include in template

```jinja
{% include "greeble/drawer.html" %}
```

```html
<div class="greeble-drawer-trigger">
  <button class="greeble-button greeble-button--primary" type="button"
          hx-get="/drawer/open" hx-target="#drawer-root" hx-swap="innerHTML">
    View launch add-ons
  </button>
  <p class="greeble-drawer-trigger__hint">Opens a right-aligned drawer describing upgrade perks.</p>
</div>
<div id="drawer-root" class="greeble-drawer-root" aria-live="polite" hx-target="this"></div>
```

```html
<div class="greeble-drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title"
     aria-describedby="drawer-description">
  <button class="greeble-drawer__backdrop" type="button" aria-label="Close drawer"
          hx-get="/drawer/close" hx-target="#drawer-root" hx-swap="innerHTML"></button>
  <aside class="greeble-drawer__panel" tabindex="-1">
    <header class="greeble-drawer__header">
      <div class="greeble-drawer__heading">
        <span class="greeble-drawer__eyebrow">Upgrade preview</span>
        <h2 id="drawer-title" class="greeble-heading-2">Launch add-ons</h2>
        <p id="drawer-description" class="greeble-drawer__description">
          Unlock priority support, workflow automation, and insights built for launch teams.
        </p>
      </div>
      <button class="greeble-icon-button greeble-drawer__close" type="button" aria-label="Close drawer"
              hx-get="/drawer/close" hx-target="#drawer-root" hx-swap="innerHTML">×</button>
    </header>
    <div class="greeble-drawer__body">
      <section class="greeble-drawer__section">
        <h3 class="greeble-heading-3">Included perks</h3>
        <ul class="greeble-drawer__list">
          <li><strong>Priority support:</strong> 24/7 escalation channel with shared Slack workspace.</li>
          <li><strong>Workflow builders:</strong> Automate approvals and checklists.</li>
          <li><strong>Insights pack:</strong> Streaming dashboards with anomaly alerts.</li>
        </ul>
      </section>
      <form class="greeble-drawer__form" hx-post="/drawer/subscribe" hx-target="#drawer-root" hx-swap="none">
        <label class="greeble-field__label" for="drawer-email">Work email</label>
        <input class="greeble-input" id="drawer-email" name="email" type="email"
               autocomplete="email" placeholder="team@workspace.com" required />
        <p class="greeble-field__hint">We’ll follow up with case studies and go-live checklists.</p>
        <div class="greeble-drawer__actions">
          <button class="greeble-button greeble-button--primary" type="submit">Request walkthrough</button>
          <button class="greeble-button greeble-button--ghost" type="button"
                  hx-get="/drawer/close" hx-target="#drawer-root" hx-swap="innerHTML">Close</button>
        </div>
      </form>
    </div>
  </aside>
</div>
```

When the user submits the form, respond with an out-of-band toast to confirm the request and
optionally close the drawer.

## Keyboard map

- Esc – Close the drawer (wire close button and backdrop to this action).
- Tab / Shift+Tab – Cycle focus within the drawer panel (focus trap).
- Enter / Space – Activate focused action, including the submit and close buttons.

## Response matrix

- GET /drawer/open
  - 200 OK — returns drawer partial
  - Headers: optional `HX-Trigger: {"greeble:drawer:open": true}`

- GET /drawer/close
  - 200 OK — returns empty string to clear `#drawer-root`
  - Headers: optional `HX-Trigger: {"greeble:drawer:close": true}`

- POST /drawer/subscribe
  - 200 OK (success) — returns out-of-band toast (and optionally clears drawer root)
  - 400 Bad Request (validation) — returns the same partial with inline errors; keep drawer mounted

## View source

- Template: [drawer.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/drawer/templates/drawer.html)
- Partial: [drawer.partial.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/drawer/templates/drawer.partial.html)
- Styles: [drawer.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/drawer/static/drawer.css)
