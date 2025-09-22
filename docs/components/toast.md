# Toasts

- Purpose: Surface transient feedback via out-of-band HTMX swaps.
- Structure: Persistent root `#greeble-toasts` (`role="region"`, `aria-live="polite"`, `aria-atomic="false"`). Returned items use `.greeble-toast` with variant modifiers (`--success`, `--info`, `--warn`, `--danger`).
- Inputs: Servers return HTML that includes dismiss buttons targeting `closest .greeble-toast`.
- Events: Optionally emit `HX-Trigger` payloads such as `{ "greeble:toast": { "level": "success" } }`.
- Accessibility: Each toast is `role="status"`; dismiss buttons include `aria-label`; icons are decorative `aria-hidden`.
- Theming hooks: Override custom properties (`--_toast-*`) or variant colors to match brand guidelines.

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
