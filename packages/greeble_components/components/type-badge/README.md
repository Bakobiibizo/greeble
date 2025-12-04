# Type Badge Component

- **Purpose:** Colored badges for indicating content/data types, categories, and statuses. Use in pipeline builders, file uploads, and data flow visualizations.
- **Inputs:** Type name as text content; optional icon.
- **Outputs:** Visual indicator only (no events).
- **Dependencies:** None.
- **Accessibility:** Color is supplemented with text labels.

## Usage

### Data Type Badges
```html
<span class="greeble-type-badge greeble-type-badge--text">text</span>
<span class="greeble-type-badge greeble-type-badge--json">json</span>
<span class="greeble-type-badge greeble-type-badge--docs">docs</span>
<span class="greeble-type-badge greeble-type-badge--image">image</span>
<span class="greeble-type-badge greeble-type-badge--audio">audio</span>
<span class="greeble-type-badge greeble-type-badge--video">video</span>
<span class="greeble-type-badge greeble-type-badge--markdown">markdown</span>
<span class="greeble-type-badge greeble-type-badge--media">media</span>
<span class="greeble-type-badge greeble-type-badge--any">any</span>
```

### Category Badges
```html
<span class="greeble-category-badge greeble-category-badge--ingestor">ingestor</span>
<span class="greeble-category-badge greeble-category-badge--generator">generator</span>
<span class="greeble-category-badge greeble-category-badge--formatter">formatter</span>
<span class="greeble-category-badge greeble-category-badge--processor">processor</span>
<span class="greeble-category-badge greeble-category-badge--tool">tool</span>
```

### Status Badges
```html
<span class="greeble-status-badge greeble-status-badge--pending">pending</span>
<span class="greeble-status-badge greeble-status-badge--running">running</span>
<span class="greeble-status-badge greeble-status-badge--success">success</span>
<span class="greeble-status-badge greeble-status-badge--error">error</span>
<span class="greeble-status-badge greeble-status-badge--warning">warning</span>
```

### Type Flow (Data Transformation)
```html
<div class="greeble-type-flow">
  <span class="greeble-type-badge greeble-type-badge--docs">docs</span>
  <span class="greeble-type-flow__arrow">→</span>
  <span class="greeble-type-badge greeble-type-badge--text">text</span>
  <span class="greeble-type-flow__arrow">→</span>
  <span class="greeble-type-badge greeble-type-badge--json">json</span>
</div>
```

### Size Variants
```html
<span class="greeble-type-badge greeble-type-badge--text greeble-type-badge--small">small</span>
<span class="greeble-type-badge greeble-type-badge--text">default</span>
<span class="greeble-type-badge greeble-type-badge--text greeble-type-badge--large">large</span>
```

### With Icon
```html
<span class="greeble-type-badge greeble-type-badge--text greeble-type-badge--with-icon">
  <svg class="greeble-type-badge__icon" viewBox="0 0 24 24">...</svg>
  text
</span>
```

### Outline Variant
```html
<span class="greeble-type-badge greeble-type-badge--text greeble-type-badge--outline">text</span>
```

## Available Types

| Type | Color | Use Case |
|------|-------|----------|
| text | Green | Plain text, strings |
| json | Amber | JSON data |
| docs | Orange | Documents (PDF, DOCX) |
| image | Blue | Images (PNG, JPG) |
| audio | Cyan | Audio files |
| video | Purple | Video files |
| markdown | Pink | Markdown content |
| media | Teal | Mixed audio/video |
| any | Gray | Accepts any type |
| file | Indigo | Generic files |
| html | Red | HTML content |
| xml | Emerald | XML data |
| csv | Green | CSV data |
| binary | Slate | Binary data |
