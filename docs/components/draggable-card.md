# Draggable Card

Draggable cards for building visual workflows and pipelines.

## Usage

```html
<div class="greeble-draggable-card" draggable="true" data-id="step-1">
  <!-- Card content -->
</div>
```

## JavaScript API

```javascript
const card = new GreebleDraggableCard(element, {
  onDragStart: (data) => { /* handle drag start */ }
});

// Create card programmatically
const card = GreebleDraggableCard.createCard({
  id: 'my-card',
  title: 'Process Step',
  category: 'transform',
  accepts: 'text',
  produces: 'json'
});
```

## Card Palette

```javascript
const palette = new GreebleCardPalette('#palette', {
  cards: [...],
  categories: ['input', 'transform', 'output']
});
```
