# Form with Validation

- Purpose: Server-validated form that replaces invalid groups.
- Inputs: Form fields; validation rules.
- Endpoints: POST /form/validate; POST /form/submit
- Events: `greeble:form:invalid`, `greeble:form:submitted`.
- Accessibility: Associate errors via aria-describedby; focus invalid.
- States: Validating, error, success.
- Theming hooks: Error colors; input borders.
