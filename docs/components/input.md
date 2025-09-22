# Inputs

- Purpose: Collect data through accessible text, email, select, and textarea controls.
- Structure: Wrap controls in `.greeble-field` with a `<label>`, optional hint `.greeble-field__hint`, and error `.greeble-field__error`.
- Validation flow: Attach `hx-post="/input/validate"` to the field wrapper and swap the group with server responses that set `greeble-field--invalid`.
- Inputs: All native form attributes plus optional `aria-describedby` for hint/error association.
- States: Default, focus, invalid (`.greeble-field--invalid`), disabled.
- Events: Servers may emit `HX-Trigger: {"greeble:validate": {...}}` after validation.
- Accessibility: Labels are always visible; errors announced via `role="alert"`; select uses custom arrow while respecting keyboard controls.
- Theming hooks: Relies on `greeble_core` tokens for radius, color, focus ring; component CSS exposes `--greeble-spacing-*` overrides.

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
