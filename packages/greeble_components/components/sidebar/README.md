# Sidebar Component

A vertical sidebar for subcategory/section navigation with collapsible groups.

## Features

- **Collapsible groups** - Expand/collapse sections
- **Scroll spy** - Auto-highlight current section
- **Smooth scroll** - Click to scroll to sections
- **Active states** - Visual indicator for current item
- **Responsive** - Hidden on mobile, can be toggled
- **Accessible** - Proper ARIA attributes

## Usage

```html
<aside class="greeble-sidebar" data-greeble-sidebar>
  <div class="greeble-sidebar__header">
    <span class="greeble-sidebar__title">Navigation</span>
  </div>

  <nav class="greeble-sidebar__nav">
    <div class="greeble-sidebar__group">
      <button
        type="button"
        class="greeble-sidebar__group-toggle"
        aria-expanded="true"
        aria-controls="group-1"
      >
        <svg class="greeble-sidebar__chevron" viewBox="0 0 24 24">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
        Group Title
      </button>
      <ul class="greeble-sidebar__list" id="group-1">
        <li class="greeble-sidebar__item">
          <a href="#section-1" class="greeble-sidebar__link">Item 1</a>
        </li>
        <li class="greeble-sidebar__item">
          <a href="#section-2" class="greeble-sidebar__link">Item 2</a>
        </li>
      </ul>
    </div>
  </nav>
</aside>
```

## Layout Integration

Typically used with nav in a two-column layout:

```html
<div class="app-layout">
  <nav class="greeble-nav">...</nav>
  <div class="app-layout__body">
    <aside class="greeble-sidebar greeble-sidebar--sticky">...</aside>
    <main class="app-layout__content">...</main>
  </div>
</div>
```

```css
.app-layout__body {
  display: flex;
}
.app-layout__content {
  flex: 1;
  min-width: 0;
}
```

## Variants

### Sticky
```html
<aside class="greeble-sidebar greeble-sidebar--sticky">...</aside>
```

### Compact
```html
<aside class="greeble-sidebar greeble-sidebar--compact">...</aside>
```

## Active States

Links are automatically highlighted via scroll spy. Manual control:

```html
<a href="#section" class="greeble-sidebar__link" data-active="true">Active</a>
```

## Badges

Add badges for counts or status:

```html
<a href="#section" class="greeble-sidebar__link">
  Item
  <span class="greeble-sidebar__badge">12</span>
</a>

<a href="#section" class="greeble-sidebar__link">
  New Feature
  <span class="greeble-sidebar__badge greeble-sidebar__badge--new">New</span>
</a>
```

## JavaScript

Include `sidebar.js` for:
- Group expand/collapse
- Scroll spy (auto-highlight)
- Smooth scroll to sections

```html
<script src="path/to/sidebar.js"></script>
```

## Responsive Behavior

- **Desktop (>1024px)**: Visible as fixed sidebar
- **Mobile (≤1024px)**: Hidden by default

To show on mobile, add `data-open="true"`:

```html
<aside class="greeble-sidebar" data-open="true">...</aside>
```

Toggle via JavaScript or HTMX.
