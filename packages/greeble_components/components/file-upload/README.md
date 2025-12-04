# File Upload Component

- **Purpose:** Multi-mode file input with tabbed interface supporting file upload, URL fetch, and paste input.
- **Inputs:** Files via drag-and-drop or browse; URLs; pasted content (text, JSON, markdown, HTML).
- **Outputs:** File object, URL string, or pasted text with auto-detected content type.
- **Dependencies:** None required; HTMX optional for server integration.
- **Endpoints:** Configurable `fetchEndpoint` for URL fetching.
- **Events:**
  - `greeble:fileupload:input` - Input changed (file, URL, or paste)
  - `greeble:fileupload:tab` - Tab switched
  - `greeble:fileupload:fetch` - URL fetch requested
  - `greeble:fileupload:error` - Error occurred
- **Accessibility:** ARIA tabs pattern, keyboard navigation, labeled inputs.

## Usage

### Basic HTML
```html
<div class="greeble-file-upload" id="file-upload" data-greeble-file-upload>
  <!-- Component HTML from template -->
</div>
```

### JavaScript Initialization
```javascript
const upload = new GreebleFileUpload('#file-upload', {
  accept: ['image/*', '.pdf', '.docx'],
  maxSize: 10 * 1024 * 1024, // 10MB
  onInput: (value, type, mode) => {
    console.log(`Mode: ${mode}, Type: ${type}`, value);
  },
  onError: (message) => {
    console.error(message);
  }
});

// Get current data
const { value, type, mode } = upload.getData();

// Clear all inputs
upload.clear();
```

### Content Type Detection

The component automatically detects content types:
- **File mode**: Based on MIME type and extension
- **URL mode**: Assumes `docs` type
- **Paste mode**: Detects JSON, Markdown, HTML, or plain text

### Type Variants

Add variant classes to customize for specific file types:
```html
<div class="greeble-file-upload greeble-file-upload--image">
<div class="greeble-file-upload greeble-file-upload--audio">
<div class="greeble-file-upload greeble-file-upload--video">
<div class="greeble-file-upload greeble-file-upload--docs">
```
