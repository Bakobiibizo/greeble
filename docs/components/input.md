# Inputs

- Purpose: Collect data through accessible text, email, select, and textarea controls.
- Structure: Wrap controls in `.greeble-field` with a `<label>`, optional hint `.greeble-field__hint`, and error `.greeble-field__error`.
- Validation flow: Attach `hx-post="/input/validate"` to the field wrapper and swap the group with server responses that set `greeble-field--invalid`.
- Inputs: All native form attributes plus optional `aria-describedby` for hint/error association.
- States: Default, focus, invalid (`.greeble-field--invalid`), disabled.
- Events: Servers may emit `HX-Trigger: {"greeble:validate": {...}}` after validation.
- Accessibility: Labels are always visible; errors announced via `role="alert"`; select uses custom arrow while respecting keyboard controls.
- Theming hooks: Relies on `greeble_core` tokens for radius, color, focus ring; component CSS exposes `--greeble-spacing-*` overrides.

## Server contract

- Validation endpoint returns the entire `.greeble-field` group with updated classes and error
  content. Return HTTP 400 when invalid so HTMX can surface the error state without leaving the
  page.
- Successful validation may remove the error copy or emit an HX trigger so other components can
  respond.
- Full form submissions typically respond with out-of-band toasts and a fresh input group to clear
  the field.

## Copy & Paste

```html
<div class="greeble-field" id="signup-email-group" hx-post="/signup/validate" hx-trigger="change delay:400ms from:#signup-email"
     hx-target="#signup-email-group" hx-include="#signup-email" hx-swap="outerHTML">
  <label class="greeble-field__label" for="signup-email">Work email</label>
  <input class="greeble-input" id="signup-email" name="email" type="email"
         autocomplete="email" aria-describedby="signup-email-hint" required />
  <p class="greeble-field__hint" id="signup-email-hint">We will send a verification link.</p>
</div>
```

Add an error block when returning invalid input:

```html
<div class="greeble-field greeble-field--invalid" id="signup-email-group" role="group"
     hx-swap-oob="true">
  <label class="greeble-field__label" for="signup-email">Work email</label>
  <input class="greeble-input" id="signup-email" name="email" type="email"
         autocomplete="email" aria-describedby="signup-email-hint signup-email-error"
         aria-invalid="true" required />
  <p class="greeble-field__hint" id="signup-email-hint">We will send a verification link.</p>
  <p class="greeble-field__error" id="signup-email-error" role="alert">Enter a valid email.</p>
</div>
```
