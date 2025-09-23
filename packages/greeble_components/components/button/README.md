# Button Component

- **Purpose:** Launch primary and secondary actions with accessible button variants.
- **Variants:** `--primary`, `--secondary`, `--ghost`, `--destructive`, `--icon`, `--loading` (spinner + disabled).
- **Inputs:** Standard button attributes; add `hx-*` to send HTMX requests.
- **Outputs:** None directly—paired endpoints return fragments or JSON.
- **Dependencies:** `greeble_core` tokens for spacing, radius, focus ring.
- **Events:** Emit HX-Trigger headers such as `{ "greeble:click": true }` when needed.
- **Accessibility:** Icon buttons require `aria-label`; loading state sets `aria-live` so screen readers announce progress.
