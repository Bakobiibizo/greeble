# Infinite List

- Purpose: Stream feed entries without pagination by appending new items when the sentinel enters the viewport.
- Structure: `<ul id="infinite-list">` holds items; a sentinel `<div>` with `hx-get="/list"` and
  `hx-trigger="revealed"` fetches additional fragments. Include a fallback “Load more” button for
  keyboard-only users.
- Endpoint: `GET /list` returns one or more `<li>` elements. Return an empty response or sentinel
  removal fragment when the feed is exhausted.
- Events: Emit `HX-Trigger: {"greeble:list:append": {"count": 3}}` so other widgets can update.
- Accessibility: Keep the list `aria-live="polite"` and ensure elements announce context (e.g., use
  `<strong>` headings, descriptive copy). Provide manual controls in addition to the sentinel.
- Theming hooks: `.greeble-feed__item`, `.greeble-feed__sentinel`, and `.greeble-feed__description`.

## Copy & Paste

```html
<section class="greeble-feed" aria-labelledby="feed-heading">
  <header class="greeble-feed__header">
    <h2 id="feed-heading" class="greeble-heading-2">Activity feed</h2>
    <p class="greeble-feed__description">Recent automation updates and background tasks.</p>
  </header>
  <ul class="greeble-feed__list" id="infinite-list" aria-live="polite">
    <li class="greeble-feed__item">
      <strong>Workflow deployed</strong>
      <span>Content calendar automation enabled for Marketing.</span>
    </li>
  </ul>
  <div id="infinite-list-sentinel" class="greeble-feed__sentinel"
       hx-get="/list" hx-trigger="revealed" hx-target="#infinite-list" hx-swap="beforeend">
    <span aria-hidden="true">Loading more…</span>
  </div>
  <button class="greeble-button greeble-button--ghost" type="button"
          hx-get="/list" hx-target="#infinite-list" hx-swap="beforeend">
    Load more updates
  </button>
</section>
```

`GET /list` returns a fragment like:

```html
<li class="greeble-feed__item">
  <strong>Automation queued</strong>
  <span>Background job #1285 completed successfully.</span>
</li>
```

## Keyboard map

- Tab / Shift+Tab – Move between list items, sentinel, and the fallback "Load more" button.
- Enter / Space – Activate the fallback "Load more" button.

## Response matrix

- GET /list
  - 200 OK — returns one or more `<li>` items appended to the list
  - 204 No Content — optional; indicates no more items (client may remove sentinel)
  - Headers: optional `HX-Trigger: {"greeble:list:append": {"count": <int>}}`
