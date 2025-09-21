# Drawer

- Purpose: Edge panel for settings/filters.
- Inputs: Open/close triggers; optional form inputs.
- Endpoints: GET /drawer/open; GET /drawer/close
- Events: `greeble:drawer:open`, `greeble:drawer:close`.
- Accessibility: role=dialog; heading label.
- States: Open/closed; busy during save.
- Theming hooks: Drawer panel, backdrop.
