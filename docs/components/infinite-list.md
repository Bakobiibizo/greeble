# Infinite List

- Purpose: Lazy loading list using revealed trigger.
- Inputs: Cursor query param.
- Endpoints: GET /list?cursor=<id>
- Events: `greeble:list:append`.
- Accessibility: Maintain position; announce new content.
- States: Idle, loading more, end of list.
- Theming hooks: List spacing; sentinel visibility.
