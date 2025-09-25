# Toasts

- Purpose: Surface transient feedback via out-of-band HTMX swaps.
- Structure: Persistent root `#greeble-toasts` (`role="region"`, `aria-live="polite"`, `aria-atomic="false"`). Returned items use `.greeble-toast` with variant modifiers (`--success`, `--info`, `--warn`, `--danger`).
- Inputs: Servers return HTML that includes dismiss buttons targeting `closest .greeble-toast`.
- Events: Optionally emit `HX-Trigger` payloads such as `{ "greeble:toast": { "level": "success" } }`.
- Accessibility: Each toast is `role="status"`; dismiss buttons include `aria-label`; icons are decorative `aria-hidden`.
- Theming hooks: Override custom properties (`--_toast-*`) or variant colors to match brand guidelines.

## Include in template

```jinja
{% include "greeble/toast.root.html" %}
{% include "greeble/toast.item.html" %}
```

## Server contract

- Any endpoint can return a toast out-of-band by wrapping the item markup in a `<div id="greeble-toasts" hx-swap-oob="true">…</div>` container.
- Use different modifiers (`greeble-toast--success`, `--info`, `--warn`, `--danger`) to signal the
  toast level.
- Include dismiss buttons that call `GET /toast/dismiss` (or your equivalent endpoint). Returning an
  empty response removes the toast element from the DOM.
- Emit optional `HX-Trigger` payloads such as `{ "greeble:toast": { "level": "info" } }` for
  analytics or to update counters elsewhere in the UI.

## Copy & Paste

```html
<div id="greeble-toasts" class="greeble-toast-region" aria-live="polite" aria-label="Notifications"></div>
```

## View source

- Root: [toast.root.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/toast/templates/toast.root.html)
- Item: [toast.item.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/toast/templates/toast.item.html)
- Styles: [toast.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/toast/static/toast.css)
## Keyboard map

- Tab / Shift+Tab – Move focus to the dismiss button.
- Enter / Space – Activate the dismiss button to remove the toast.

## Response matrix

- Any endpoint returning a toast out-of-band
  - 200 OK — returns toast markup wrapped in `<div id="greeble-toasts" hx-swap-oob="true">…</div>`
  - Headers: optional `HX-Trigger: {"greeble:toast": {"level": "success" | "info" | "warn" | "danger"}}`

- GET /toast/dismiss (example)
  - 200 OK — returns empty response; client swaps out the toast via `hx-target="closest .greeble-toast"`

```html
<div id="greeble-toasts" hx-swap-oob="true">
  <div class="greeble-toast greeble-toast--success" role="status">
    <div class="greeble-toast__icon" aria-hidden="true">✔</div>
    <div class="greeble-toast__body">
      <p class="greeble-toast__title">Settings saved</p>
      <p class="greeble-toast__message">Your updates are live.</p>
    </div>
    <button class="greeble-icon-button greeble-toast__dismiss" aria-label="Dismiss" hx-get="/toast/dismiss" hx-target="closest .greeble-toast" hx-swap="outerHTML">×</button>
  </div>
</div>
```
