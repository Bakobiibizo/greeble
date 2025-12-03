# Swap Select Component

- **Purpose:** Paired select dropdowns with a swap button to exchange values. Ideal for source/target selection (languages, units, currencies).
- **Inputs:** Two select elements with options loaded via HTMX or static HTML.
- **Outputs:** Selected values from both dropdowns; swap events.
- **Dependencies:** HTMX (optional for dynamic options loading).
- **Endpoints:** `GET /options/source`, `GET /options/target` (configurable).
- **Events:**
  - `greeble:swap:swapped` - Values were swapped
  - `greeble:swap:change` - Either select value changed
- **Accessibility:** Labels for selects, keyboard shortcut (Ctrl+Shift+S) to swap.

## Usage

### Basic HTML
```html
<div class="greeble-swap-select" id="swap-select" data-greeble-swap-select>
  <div class="greeble-swap-select__field">
    <label class="greeble-swap-select__label" for="swap-select-left">From</label>
    <select id="swap-select-left" class="greeble-swap-select__select">
      <option value="usd">USD</option>
      <option value="eur">EUR</option>
      <option value="gbp">GBP</option>
    </select>
  </div>
  
  <button type="button" class="greeble-swap-select__swap" id="swap-select-button">
    <!-- swap icon -->
  </button>
  
  <div class="greeble-swap-select__field">
    <label class="greeble-swap-select__label" for="swap-select-right">To</label>
    <select id="swap-select-right" class="greeble-swap-select__select">
      <option value="usd">USD</option>
      <option value="eur" selected>EUR</option>
      <option value="gbp">GBP</option>
    </select>
  </div>
</div>
```

### JavaScript Initialization
```javascript
const swapSelect = new GreebleSwapSelect('#swap-select', {
  preventSameValue: true, // Don't allow both to have same value
  onSwap: (left, right) => {
    console.log(`Swapped: ${left} <-> ${right}`);
  },
  onChange: (side, value) => {
    console.log(`${side} changed to ${value}`);
  }
});

// Programmatic control
swapSelect.swap();
swapSelect.setValues('en', 'es');
const { left, right } = swapSelect.getValues();
```

### With HTMX Dynamic Loading
```html
<select
  id="swap-select-left"
  hx-get="/api/languages"
  hx-trigger="load"
  hx-target="#swap-select-left"
  hx-swap="innerHTML"
>
  <option value="">Loading...</option>
</select>
```

## Variants

### Vertical Layout
```html
<div class="greeble-swap-select greeble-swap-select--vertical">
```

### Compact (No Labels)
```html
<div class="greeble-swap-select greeble-swap-select--compact">
```
