# Draggable Card Component

- **Purpose:** Draggable card for building pipeline/workflow interfaces. Use with drop-canvas for complete drag-and-drop UIs.
- **Inputs:** Card data (id, category, accepts, produces); drag events.
- **Outputs:** Drag data in JSON format; compatibility highlighting.
- **Dependencies:** None required.
- **Events:**
  - `greeble:card:dragstart` - Card drag started
  - `greeble:card:dragend` - Card drag ended
- **Accessibility:** Native draggable attribute, keyboard support via browser.

## Usage

### Basic Card
```html
<div
  class="greeble-draggable-card greeble-draggable-card--processor"
  draggable="true"
  data-greeble-draggable
  data-id="my-card"
  data-category="processor"
  data-accepts="text,json"
  data-produces="text"
>
  <div class="greeble-draggable-card__header">
    <span class="greeble-draggable-card__icon">⚙️</span>
    <span class="greeble-draggable-card__title">My Processor</span>
  </div>
  <div class="greeble-draggable-card__types">
    <span class="greeble-type-badge greeble-type-badge--text">text</span>
    <span class="greeble-draggable-card__arrow">→</span>
    <span class="greeble-type-badge greeble-type-badge--text">text</span>
  </div>
</div>
```

### Card Palette
```javascript
const palette = new GreebleCardPalette('#palette', {
  cards: [
    {
      id: 'file-reader',
      category: 'ingestor',
      icon: '📄',
      title: 'File Reader',
      accepts: ['file'],
      produces: 'text',
      inputType: 'docs',
      inputLabel: 'file',
      outputType: 'text',
      outputLabel: 'text'
    },
    {
      id: 'llm-generator',
      category: 'generator',
      icon: '🤖',
      title: 'LLM Generator',
      accepts: ['text'],
      produces: 'text'
    }
  ],
  onCardDragStart: (data) => {
    console.log('Dragging:', data);
  }
});

// Highlight compatible cards
palette.highlightCompatible('text');

// Filter cards
palette.filter('reader');
```

### Create Card Programmatically
```javascript
const card = GreebleDraggableCard.createCard({
  id: 'new-card',
  category: 'tool',
  icon: '🔧',
  title: 'New Tool',
  accepts: ['any'],
  produces: 'json'
}, { container: document.querySelector('#cards') });
```

## Category Variants

- `greeble-draggable-card--ingestor` (Blue)
- `greeble-draggable-card--generator` (Purple)
- `greeble-draggable-card--formatter` (Green)
- `greeble-draggable-card--processor` (Pink)
- `greeble-draggable-card--tool` (Orange)

## Type Badges

Built-in type badge styles:
- `greeble-type-badge--text` (Green)
- `greeble-type-badge--docs` (Orange)
- `greeble-type-badge--image` (Blue)
- `greeble-type-badge--audio` (Cyan)
- `greeble-type-badge--video` (Purple)
- `greeble-type-badge--json` (Amber)
- `greeble-type-badge--markdown` (Pink)
- `greeble-type-badge--media` (Teal)
- `greeble-type-badge--any` (Gray)
