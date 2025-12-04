# Drop Zone

File drop zone with drag-and-drop support and file list management.

## Usage

```html
<div data-greeble-drop-zone>
  <p>Drop files here or click to browse</p>
</div>
```

## JavaScript API

```javascript
const dropZone = new GreebleDropZone('#drop-zone', {
  accept: ['image/*', '.pdf'],
  maxFiles: 5,
  maxSize: 10 * 1024 * 1024, // 10MB
  onFilesAdded: (files) => { /* handle files */ }
});
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `accept` | `array` | `['*']` | Accepted file types |
| `maxFiles` | `number` | `10` | Maximum number of files |
| `maxSize` | `number` | `null` | Maximum file size in bytes |
| `onFilesAdded` | `function` | `null` | Callback when files are added |
| `onFileRemoved` | `function` | `null` | Callback when file is removed |

## Events

- `greeble:dropzone:change` - Files changed
