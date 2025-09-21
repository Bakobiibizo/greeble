# Toasts (Placeholder)
- **Purpose:** Global toast queue using out-of-band swaps.
- **Inputs:** Any server event may return toast fragments.
- **Outputs:** Toast root and items.
- **Dependencies:** HTMX; greeble_core.
- **Events:** `greeble:toast`
- **Accessibility:** aria-live=assertive on root; dismiss buttons with labels.
