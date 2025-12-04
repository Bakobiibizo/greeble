# Swap Select

Dual select boxes with swap functionality for comparing or exchanging values.

## Usage

```html
<div data-greeble-swap-select>
  <select data-side="left">
    <option value="a">Option A</option>
    <option value="b">Option B</option>
  </select>
  <button data-swap>⇄</button>
  <select data-side="right">
    <option value="a">Option A</option>
    <option value="b">Option B</option>
  </select>
</div>
```

## JavaScript API

```javascript
const swapSelect = new GreebleSwapSelect('#swap-select', {
  onChange: (side, value) => { /* handle change */ },
  onSwap: (leftValue, rightValue) => { /* handle swap */ }
});

// Programmatic control
swapSelect.swap();
swapSelect.setLeftValue('a');
swapSelect.setRightValue('b');
swapSelect.setOptions([
  { value: 'x', label: 'Option X' },
  { value: 'y', label: 'Option Y', selected: true }
]);
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `onChange` | `function` | `null` | Selection change callback |
| `onSwap` | `function` | `null` | Swap action callback |
