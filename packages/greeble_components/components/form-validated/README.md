# Validated Form

- **Purpose:** Collect input with server-side validation and HTMX-driven feedback.
- **Structure:** `form.html` contains the full form and the email group that re-renders via
  `/form/validate`. `/form/submit` handles the final submission and updates `#form-status` (and can
  send out-of-band toasts).
- **Endpoints:**
  - `POST /form/validate` → returns the email field group with updated classes and errors.
  - `POST /form/submit` → returns success copy (and optional toast) or the invalid group.
- **Events:** Emit `HX-Trigger: {"greeble:form:invalid": {"field": "email"}}` on validation errors
  and `{"greeble:form:submitted": true}` when the form completes.
- **Accessibility:** Error messages are linked via `aria-describedby` and announced with
  `role="alert"`. The invalid group sets `aria-invalid="true"`.
- **Theming:** `.greeble-validated-form__body`, `.greeble-validated-form__actions`, and
  `.greeble-field--invalid` can be themed to match your design system.
