# Footer Component

A page footer with multi-column links, branding, and social links.

## Features

- **Multi-column layout** - Organized link groups
- **Brand section** - Logo, tagline, and social links
- **Responsive** - Stacks on mobile
- **Variants** - Compact and minimal options

## Usage

```html
<footer class="greeble-footer">
  <div class="greeble-footer__container">
    <div class="greeble-footer__main">
      <!-- Brand -->
      <div class="greeble-footer__brand">
        <a href="/" class="greeble-footer__logo">
          <span class="greeble-footer__logo-text">Brand</span>
        </a>
        <p class="greeble-footer__tagline">Your tagline here.</p>
        <div class="greeble-footer__social">
          <a href="#" class="greeble-footer__social-link" aria-label="GitHub">
            <svg>...</svg>
          </a>
        </div>
      </div>

      <!-- Links -->
      <div class="greeble-footer__links">
        <div class="greeble-footer__column">
          <h4 class="greeble-footer__heading">Column 1</h4>
          <ul class="greeble-footer__list">
            <li><a href="#" class="greeble-footer__link">Link 1</a></li>
            <li><a href="#" class="greeble-footer__link">Link 2</a></li>
          </ul>
        </div>
        <!-- More columns... -->
      </div>
    </div>

    <!-- Bottom bar -->
    <div class="greeble-footer__bottom">
      <p class="greeble-footer__copyright">&copy; 2024 Brand</p>
      <div class="greeble-footer__meta">
        <span class="greeble-footer__version">v1.0.0</span>
      </div>
    </div>
  </div>
</footer>
```

## Variants

### Compact
Reduced padding and spacing:
```html
<footer class="greeble-footer greeble-footer--compact">...</footer>
```

### Minimal
Only shows the bottom bar:
```html
<footer class="greeble-footer greeble-footer--minimal">...</footer>
```

## Customization

### Adding Newsletter Signup

Integrate with the form-validated component:

```html
<div class="greeble-footer__brand">
  <!-- ... logo and tagline ... -->
  
  <form class="greeble-footer__newsletter" hx-post="/newsletter/subscribe">
    <input type="email" placeholder="Enter your email" class="greeble-input" />
    <button type="submit" class="greeble-button greeble-button--primary">
      Subscribe
    </button>
  </form>
</div>
```

### Custom Columns

Add or remove columns as needed:

```html
<div class="greeble-footer__links">
  <div class="greeble-footer__column">...</div>
  <div class="greeble-footer__column">...</div>
  <div class="greeble-footer__column">...</div>
  <div class="greeble-footer__column">...</div>
</div>
```

Adjust grid in CSS:
```css
.greeble-footer__links {
  grid-template-columns: repeat(4, 1fr);
}
```

## Responsive Behavior

- **Desktop**: Multi-column layout
- **Tablet (≤768px)**: 2-column links, stacked brand
- **Mobile (≤480px)**: Single column

## No JavaScript Required

This component is purely CSS-based and doesn't require JavaScript.
