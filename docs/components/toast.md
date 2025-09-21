# Toasts

- Purpose: Global toast queue (OOB swaps).
- Inputs: Messages from server events.
- Endpoints: Any endpoint may return toast OOB fragments.
- Events: `greeble:toast`.
- Accessibility: aria-live=assertive; labeled dismiss.
- States: Info/success/warn/error variants; timeout.
- Theming hooks: Toast colors; shadows.
