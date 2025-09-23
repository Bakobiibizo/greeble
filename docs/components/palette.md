# Command Palette

- Purpose: Provide a keyboard-driven launcher for commands, invite flows, or navigation.
- Structure: A search `<form>` posts to `/palette/search` and swaps results into `#palette-results`.
  Each result button posts to `/palette/select`, replacing `#palette-detail` with contextual info.
- Endpoints: `POST /palette/search`, `POST /palette/select`.
- Events: `HX-Trigger` payloads such as `{"greeble:palette:select": {"command": "invite"}}` keep
  other components in sync.
- Accessibility: Results render as `role="listbox"` with `role="option"` items. Maintain
  `aria-selected` on the active option and announce updates via `aria-live`.
- Theming hooks: `.greeble-palette__result`, `.greeble-palette__detail`, `.greeble-palette__layout`,
  and `.greeble-palette__form` expose layout and colour customisation points.

## Copy & Paste

```html
<section class="greeble-palette" aria-labelledby="palette-heading">
  <header class="greeble-palette__header">
    <h2 id="palette-heading" class="greeble-heading-2">Command palette</h2>
    <p class="greeble-palette__description">
      Search shortcuts, people, and workspaces. Use arrow keys to move through the results and
      <kbd>Enter</kbd> to select.
    </p>
  </header>

  <form class="greeble-palette__form" role="search"
        hx-post="/palette/search"
        hx-trigger="submit, keyup changed delay:250ms from:input[name=q]"
        hx-target="#palette-results" hx-swap="innerHTML">
    <label class="greeble-field__label" for="palette-query">Search commands</label>
    <input class="greeble-input" id="palette-query" name="q" type="search"
           placeholder="Search by command, teammate, or workspace" aria-describedby="palette-hint" />
    <p class="greeble-field__hint" id="palette-hint">Try typing "invite" or ":settings"</p>
  </form>

  <div class="greeble-palette__layout">
    <div class="greeble-palette__results" role="region" aria-live="polite">
      <h3 class="greeble-heading-3">Results</h3>
      <div id="palette-results" role="listbox" aria-label="Command results">
        <p class="greeble-palette__empty">Start typing to see matches.</p>
      </div>
    </div>
    <div id="palette-detail" class="greeble-palette__detail" aria-live="polite">
      <h3 class="greeble-heading-3">Selection</h3>
      <p>Select a result to preview details.</p>
    </div>
  </div>
</section>
```

Results endpoint returns the listbox structure:

```html
<ul class="greeble-palette__list" role="listbox" aria-label="Command results">
  <li role="option" data-command="open-project" aria-selected="true">
    <button class="greeble-palette__result" type="button"
            hx-post="/palette/select" hx-target="#palette-detail" hx-swap="innerHTML"
            hx-vals='{"command": "open-project"}'>
      <div class="greeble-palette__result-label">
        <strong>Open project overview</strong>
        <span>Jump to dashboards and launch metrics.</span>
      </div>
      <span class="greeble-palette__result-kbd">⌘ + K → P</span>
    </button>
  </li>
  <!-- additional results -->
</ul>
```

Adjust the copy and command payloads to match your product taxonomy.

## Keyboard map

- ⌘/Ctrl + K – Open command palette (binding provided by your app shell).
- Arrow Up/Down – Move focus between results.
- Enter – Select the focused result.
- Esc – Close the palette and return focus to the trigger.
- Tab / Shift+Tab – Move between the search input and results; keep focus within the palette while open.

## Response matrix

- POST /palette/search
  - 200 OK — returns results listbox (role=listbox with role=option items)
  - Headers: `HX-Trigger: {"greeble:palette:results": {"count": <int>}}` (optional)

- POST /palette/select
  - 200 OK — returns detail panel content for the selected item
  - Headers: `HX-Trigger: {"greeble:palette:select": {"command": "<key>"}}`
