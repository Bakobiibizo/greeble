# Button

- Purpose: Launch key actions with accessible, theme-aware buttons.
- Variants: `greeble-button--primary`, `--secondary`, `--ghost`, `--destructive`, `--icon`, `--loading`.
- Inputs: Standard button/anchor attributes; optional `data-variant` metadata; add `hx-*` to integrate with HTMX endpoints.
- States: Default, hover, active, focus-visible, disabled, loading (shows spinner).
- Events: Emits `greeble:click` (optional) via HX-Trigger headers.
- Accessibility: Uses native `<button>` semantics; icon buttons require `aria-label`; loading buttons set `aria-live` and `disabled`.
- Theming hooks: Relies on `greeble_core` tokens; override `--_btn-*` custom properties per variant.

## Server integration

- Buttons are usually paired with HTMX attributes (`hx-get`, `hx-post`, `hx-delete`) that target a
  container (`hx-target`) and define the swap behaviour (`hx-swap`).
- Emit additional metadata with `hx-vals='{"key": "value"}'` when the server needs structured
  payloads.
- Use `HX-Trigger` headers in the response to emit `greeble:click` (or any custom event) so other
  components can react.

## Copy & Paste

```html
<button class="greeble-button greeble-button--primary" type="submit">Save changes</button>
<button class="greeble-button greeble-button--ghost" type="button" hx-get="/modal/example" hx-target="#modal-root">Preview</button>
```

Wrap a cluster of buttons in `.greeble-button-group` to space them evenly.

## Keyboard map

- Tab / Shift+Tab – Move focus between buttons.
- Enter / Space – Activate the focused button.

## Response matrix

- Typical HTMX endpoints (e.g., GET/POST/DELETE)
  - 200 OK — returns a fragment for the target region; may include out-of-band updates and `HX-Trigger` payloads
  - 4xx — return inline error fragment or toast guidance; keep focus handling consistent
