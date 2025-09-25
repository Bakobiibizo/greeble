# Form with Validation

- Purpose: Validate inputs on the server while keeping the user in flow.
- Structure: `.greeble-validated-form` wraps the header, form body, and status area. The email group
  uses HTMX to swap itself with the server response when the user edits the field.
- Endpoints: `POST /form/validate`, `POST /form/submit`.
- Events: Emit `HX-Trigger: {"greeble:form:invalid": {"field": "email"}}` when returning an
  invalid group and `HX-Trigger: {"greeble:form:submitted": true}` on success.
- Accessibility: Each error is associated with the field via `aria-describedby` and announced with
  `role="alert"`. Keep the status region `aria-live="polite"`.
- Theming hooks: `.greeble-validated-form__body`, `.greeble-field--invalid`, and
  `.greeble-validated-form__actions`.

## Copy & Paste

```html
<section class="greeble-validated-form" aria-labelledby="signup-heading">
  <header class="greeble-validated-form__header">
    <h2 id="signup-heading" class="greeble-heading-2">Request early access</h2>
    <p>We’ll review your workspace and send a magic link once you’re approved.</p>
  </header>
  <form class="greeble-validated-form__body" hx-post="/form/submit" hx-target="#form-status" hx-swap="innerHTML">
    <div class="greeble-field">
      <label class="greeble-field__label" for="form-name">Full name</label>
      <input class="greeble-input" id="form-name" name="name" type="text" autocomplete="name" required />
    </div>
    <div id="form-email-group" class="greeble-field"
         hx-post="/form/validate"
         hx-trigger="change from:#form-email, keyup delay:400ms from:#form-email, blur from:#form-email"
         hx-target="#form-email-group" hx-swap="outerHTML" hx-include="#form-email">
      <label class="greeble-field__label" for="form-email">Work email</label>
      <input class="greeble-input" id="form-email" name="email" type="email"
             autocomplete="email" aria-describedby="form-email-hint" required />
      <p class="greeble-field__hint" id="form-email-hint">Use your company domain for faster approval.</p>
    </div>
    <label class="greeble-checkbox">
      <input class="greeble-checkbox__input" type="checkbox" name="updates" value="1" checked />
      <span class="greeble-checkbox__label">Send me product updates and launch resources.</span>
    </label>
    <div class="greeble-validated-form__actions">
      <button class="greeble-button greeble-button--primary" type="submit">Request access</button>
      <span class="greeble-validated-form__support">We respond within 1–2 business days.</span>
    </div>
  </form>
  <div id="form-status" class="greeble-validated-form__status" aria-live="polite"></div>
</section>
```

Invalid response example:

```html
<div id="form-email-group" class="greeble-field greeble-field--invalid" role="group"
     hx-swap-oob="true">
  <label class="greeble-field__label" for="form-email">Work email</label>
  <input class="greeble-input" id="form-email" name="email" type="email"
         autocomplete="email" aria-describedby="form-email-hint form-email-error" aria-invalid="true" required />
  <p class="greeble-field__hint" id="form-email-hint">Use your company domain for faster approval.</p>
  <p class="greeble-field__error" id="form-email-error" role="alert">Enter a valid work email.</p>
</div>
```

## Keyboard map

- Tab / Shift+Tab – Move between fields, inline errors, status region, and submit controls.
- Enter – Submit the form from a focused submit button or when within a single-line input.
- Esc – Optional: cancel or clear pending validation; app-specific behaviour.

## Response matrix

- POST /form/validate
  - 200 OK (valid) — returns a valid field group or a dedicated "valid" group; may emit `HX-Trigger: {"greeble:form:valid": {"field": "email"}}`
  - 400 Bad Request (invalid) — returns `.greeble-field.greeble-field--invalid` with error; HTMX swaps the group

- POST /form/submit
  - 200 OK — returns out-of-band toast and a cleared input group; may update `#form-status`
  - 400 Bad Request — returns original partial with error states; preserves user input

## View source

- Template: [form.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/form-validated/templates/form.html)
- Partial: [form.partial.html](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/form-validated/templates/form.partial.html)
- Styles: [form.css](https://github.com/Bakobiibizo/greeble/blob/main/packages/greeble_components/components/form-validated/static/form.css)
