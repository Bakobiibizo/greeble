# Form with Validation

- Purpose: Server-validated form that replaces invalid groups.
- Inputs: Form fields; validation rules.
- Endpoints: POST /form/validate; POST /form/submit
- Events: `greeble:form:invalid`, `greeble:form:submitted`.
- Accessibility: Associate errors via aria-describedby; focus invalid.
- States: Validating, error, success.
- Theming hooks: Error colors; input borders.

## Copy & Paste Usage

Markup:

```html
<form class="stack" hx-post="/form/submit">
  <div id="email-group"
       hx-post="/form/validate"
       hx-trigger="change from:#email, keyup delay:500ms from:#email, blur from:#email"
       hx-include="#email"
       hx-target="#email-group"
       hx-swap="outerHTML">
    <label class="greeble-label" for="email">Email</label>
    <input id="email" name="email" type="email" class="greeble-input" aria-describedby="email-help" required />
    <div id="email-help" class="visually-hidden">Enter a valid email</div>
  </div>
  <button class="greeble-button" type="submit">Submit</button>
  <!-- Optional toast root for success messages: -->
  <!-- <div id="greeble-toasts" aria-live="assertive"></div> -->
</form>
```

Server contracts:
- `POST /form/validate` returns the `#email-group` fragment (400 on invalid, 200 on valid). You may emit `HX-Trigger` like `{"greeble:form:invalid": {"field": "email"}}`.
- `POST /form/submit` returns overall success (e.g., OOB toast) or invalid group fragment.
