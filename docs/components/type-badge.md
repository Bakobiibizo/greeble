# Type Badge

Visual badges for displaying data types in pipeline/workflow UIs.

## Usage

```html
<span class="greeble-type-badge greeble-type-badge--text">text</span>
<span class="greeble-type-badge greeble-type-badge--json">json</span>
<span class="greeble-type-badge greeble-type-badge--image">image</span>
```

## Available Types

| Type | Class Modifier | Description |
|------|----------------|-------------|
| `text` | `--text` | Plain text data |
| `json` | `--json` | JSON structured data |
| `markdown` | `--markdown` | Markdown content |
| `image` | `--image` | Image data |
| `audio` | `--audio` | Audio data |
| `docs` | `--docs` | Documentation |
| `any` | `--any` | Any type accepted |

## Styling

Type badges use CSS custom properties for theming:

```css
.greeble-type-badge {
  --greeble-badge-bg: var(--greeble-color-surface);
  --greeble-badge-text: var(--greeble-color-text);
}
```
