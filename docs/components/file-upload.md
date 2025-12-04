# File Upload

Multi-mode file upload with tabbed interface for file, URL, and paste input methods.

## Usage

```html
<div data-greeble-file-upload>
  <!-- Tabs and panels render here -->
</div>
```

## JavaScript API

```javascript
const upload = new GreebleFileUpload('#file-upload', {
  onFileSelected: (file) => { /* handle file */ },
  onUrlFetched: (url) => { /* handle URL */ },
  onPaste: (content, type) => { /* handle paste */ }
});

// Get current data
const data = upload.getData();
// Returns: { mode: 'file'|'url'|'paste', value: ..., type: ... }
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accept` | `string` | `'*'` | Accepted file types |
| `maxSize` | `number` | `null` | Maximum file size |
| `onFileSelected` | `function` | `null` | File selection callback |
| `onUrlFetched` | `function` | `null` | URL fetch callback |
| `onPaste` | `function` | `null` | Paste callback |

## Paste Type Detection

The component automatically detects paste content type:
- `json` - Valid JSON
- `markdown` - Markdown syntax
- `docs` - Documentation patterns
- `text` - Plain text (default)
