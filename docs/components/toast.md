# Toasts

- Purpose: Global toast queue (OOB swaps).
- Inputs: Messages from server events.
- Endpoints: Any endpoint may return toast OOB fragments.
- Events: `greeble:toast`.
- Accessibility: aria-live=assertive; labeled dismiss.
- States: Info/success/warn/error variants; timeout.
- Theming hooks: Toast colors; shadows.

## Copy & Paste Usage

- Include the root once in your layout:
  ```html
  <div id="greeble-toasts" aria-live="assertive"></div>
  ```
- Return an item out-of-band from any endpoint:
  ```html
  <div id="greeble-toasts" hx-swap-oob="true">
    <div class="greeble-toast greeble-toast--success" role="status">Saved!</div>
  </div>
  ```
- Dismiss pattern (endpoint returns empty string):
  ```html
  <button hx-get="/toast/dismiss" hx-target="closest .greeble-toast" hx-swap="outerHTML">×</button>
  ```
- Servers may emit `HX-Trigger` headers (e.g., `{"greeble:toast": {"level":"success"}}`).
