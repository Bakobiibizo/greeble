# Infinite List

- **Purpose:** Append activity feed items as the user scrolls.
- **Structure:** `infinite-list.html` renders the initial `<ul>` plus a sentinel div that requests
  more items when revealed. The fallback “Load more updates” button triggers the same endpoint for
  keyboard users.
- **Endpoint:** `GET /list` returns a fragment containing one or more `<li class="greeble-feed__item">`
  entries to append to the list.
- **Events:** Optionally emit `HX-Trigger: {"greeble:list:append": {"count": 3}}` to update counters.
- **Accessibility:** The `<ul>` is `aria-live="polite"`; new items use standard `<strong>`/`<span>`
  markup so screen readers announce them. Keep the sentinel focusable if you offer a keyboard-only
  fallback.
- **Theming:** Override `.greeble-feed__item`, `.greeble-feed__sentinel`, and spacing tokens for
  custom styling.
