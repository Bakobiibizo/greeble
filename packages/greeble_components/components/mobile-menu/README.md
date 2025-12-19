# Mobile Menu Component

A slide-in mobile menu with user profile section and navigation links.

## Features

- **Slide-in animation** - Smooth entrance from left (or right)
- **User profile section** - Avatar, name, and email display
- **Focus trap** - Keyboard navigation stays within menu
- **Backdrop close** - Click outside to close
- **HTMX integration** - Load/close via HTMX requests
- **Accessible** - Proper ARIA roles and keyboard support

## Usage

### Container (add to your page)

```html
<div id="mobile-menu-root"></div>
```

### Trigger (in your nav)

```html
<button
  type="button"
  class="greeble-nav__toggle"
  hx-get="/menu/open"
  hx-target="#mobile-menu-root"
  hx-swap="innerHTML"
>
  <svg viewBox="0 0 24 24">
    <line x1="3" y1="6" x2="21" y2="6"/>
    <line x1="3" y1="12" x2="21" y2="12"/>
    <line x1="3" y1="18" x2="21" y2="18"/>
  </svg>
</button>
```

### Menu Content (returned by server)

```html
<div class="greeble-mobile-menu" data-greeble-mobile-menu>
  <button class="greeble-mobile-menu__backdrop" hx-get="/menu/close" hx-target="#mobile-menu-root"></button>
  
  <div class="greeble-mobile-menu__panel">
    <div class="greeble-mobile-menu__header">
      <span class="greeble-mobile-menu__title">Menu</span>
      <button class="greeble-mobile-menu__close" hx-get="/menu/close" hx-target="#mobile-menu-root">×</button>
    </div>
    
    <div class="greeble-mobile-menu__profile">
      <div class="greeble-mobile-menu__avatar">...</div>
      <div class="greeble-mobile-menu__user">
        <span class="greeble-mobile-menu__name">User Name</span>
        <span class="greeble-mobile-menu__email">user@example.com</span>
      </div>
    </div>
    
    <nav class="greeble-mobile-menu__nav">
      <ul class="greeble-mobile-menu__list">
        <li class="greeble-mobile-menu__item">
          <a href="#section" class="greeble-mobile-menu__link">
            <svg class="greeble-mobile-menu__icon">...</svg>
            Link Text
          </a>
        </li>
      </ul>
    </nav>
  </div>
</div>
```

## Variants

### Right-side slide

```html
<div class="greeble-mobile-menu greeble-mobile-menu--right">...</div>
```

## Server Endpoints

### Open Menu
```
GET /menu/open
Returns: mobile-menu.html content
```

### Close Menu
```
GET /menu/close
Returns: empty string (clears #mobile-menu-root)
```

## JavaScript

Include `mobile-menu.js` for:
- Focus trap within menu
- Escape key to close
- Body scroll lock
- Cleanup on removal

```html
<script src="path/to/mobile-menu.js"></script>
```

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Move focus forward (trapped in menu) |
| `Shift+Tab` | Move focus backward (trapped in menu) |
| `Escape` | Close menu |

## Why "Hamburger"?

The ☰ icon is called a "hamburger menu" because the three horizontal lines resemble a hamburger: bun, patty, bun. The name was coined around 2009 and stuck despite being a bit silly. Alternative names include "nav drawer", "slide menu", or just "mobile menu".
