# Button

- Purpose: Launch key actions with accessible, theme-aware buttons.
- Variants: `greeble-button--primary`, `--secondary`, `--ghost`, `--destructive`, `--icon`, `--loading`.
- Inputs: Standard button/anchor attributes; optional `data-variant` metadata; add `hx-*` to integrate with HTMX endpoints.
- States: Default, hover, active, focus-visible, disabled, loading (shows spinner).
- Events: Emits `greeble:click` (optional) via HX-Trigger headers.
- Accessibility: Uses native `<button>` semantics; icon buttons require `aria-label`; loading buttons set `aria-live` and `disabled`.
- Theming hooks: Relies on `greeble_core` tokens; override `--_btn-*` custom properties per variant.

## Copy & Paste

```html
<button class="greeble-button greeble-button--primary" type="submit">Save changes</button>
<button class="greeble-button greeble-button--ghost" type="button" hx-get="/modal/example" hx-target="#modal-root">Preview</button>
```

Wrap a cluster of buttons in `.greeble-button-group` to space them evenly.
