# Nav Component

A responsive top navigation bar with category links, mobile toggle, and scroll spy support.

## Features

- **Responsive** - Collapses to hamburger menu on mobile
- **Scroll spy** - Automatically highlights active section
- **Sticky positioning** - Stays at top while scrolling
- **HTMX integration** - Mobile menu can load via HTMX
- **Accessible** - Proper ARIA roles and keyboard navigation

## Usage

```html
<nav class="greeble-nav" id="greeble-nav" data-greeble-nav>
  <!-- Brand/Logo -->
  <div class="greeble-nav__brand">
    <a href="/" class="greeble-nav__logo">
      <span class="greeble-nav__logo-text">Brand</span>
    </a>
  </div>

  <!-- Mobile toggle -->
  <button type="button" class="greeble-nav__toggle" aria-label="Toggle navigation">
    <svg class="greeble-nav__toggle-icon" viewBox="0 0 24 24">
      <line x1="3" y1="6" x2="21" y2="6"/>
      <line x1="3" y1="12" x2="21" y2="12"/>
      <line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  </button>

  <!-- Navigation links -->
  <div class="greeble-nav__menu">
    <ul class="greeble-nav__list" role="menubar">
      <li class="greeble-nav__item" role="none">
        <a href="#section-1" class="greeble-nav__link" role="menuitem">Section 1</a>
      </li>
      <li class="greeble-nav__item" role="none">
        <a href="#section-2" class="greeble-nav__link" role="menuitem">Section 2</a>
      </li>
    </ul>
  </div>

  <!-- Actions -->
  <div class="greeble-nav__actions">
    <a href="/login" class="greeble-button greeble-button--ghost">Login</a>
  </div>
</nav>
```

## Variants

### Sticky (default)
```html
<nav class="greeble-nav greeble-nav--sticky">...</nav>
```

### Fixed
```html
<nav class="greeble-nav greeble-nav--fixed">...</nav>
```

### Transparent (for hero sections)
```html
<nav class="greeble-nav greeble-nav--transparent">...</nav>
```

## Active States

Links are automatically highlighted via scroll spy when using `href="#section-id"`. You can also manually set active state:

```html
<a href="#section" class="greeble-nav__link" data-active="true">Active Link</a>
```

Or use `aria-current`:
```html
<a href="/page" class="greeble-nav__link" aria-current="page">Current Page</a>
```

## JavaScript

Include `nav.js` for:
- Mobile menu toggle
- Scroll spy (auto-highlight sections)
- Keyboard navigation (Escape to close)
- Click outside to close

```html
<script src="path/to/nav.js"></script>
```

## HTMX Integration

The mobile toggle can load a full mobile menu via HTMX:

```html
<button
  class="greeble-nav__toggle"
  hx-get="/menu/open"
  hx-target="#mobile-menu-root"
  hx-swap="innerHTML"
>
  ...
</button>
```

## CSS Custom Properties

| Property | Default | Description |
|----------|---------|-------------|
| `--greeble-accent` | `#93c5fd` | Accent color for active states |
