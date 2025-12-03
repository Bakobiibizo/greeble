# Drop Zone Component

- **Purpose:** Drag-and-drop file upload area with file validation, preview list, and HTMX upload support.
- **Inputs:** Files via drag-and-drop or click-to-browse; configurable accept types and max size.
- **Outputs:** File list with metadata; FormData for upload.
- **Dependencies:** HTMX (optional for upload).
- **Endpoints:** `POST /files/upload` (configurable via `hx-post`).
- **Events:**
  - `greeble:dropzone:files` - Files selected/added
  - `greeble:dropzone:remove` - File removed
  - `greeble:dropzone:clear` - All files cleared
  - `greeble:dropzone:upload` - Upload initiated
  - `greeble:dropzone:error` - Validation error
- **Accessibility:** `aria-describedby` for help text, keyboard accessible via hidden file input.

## Usage

### Basic HTML
```html
<div
  class="greeble-drop-zone"
  id="drop-zone"
  data-greeble-drop-zone
  data-accept=".pdf,.docx,.txt"
  data-max-size="10485760"
  data-multiple="true"
>
  <!-- Component HTML from template -->
</div>
```

### JavaScript Initialization
```javascript
const dropZone = new GreebleDropZone('#drop-zone', {
  accept: ['.pdf', '.docx', 'image/*'],
  maxSize: 10 * 1024 * 1024, // 10MB
  multiple: true,
  onFilesSelected: (files) => {
    console.log('Files selected:', files);
  },
  onError: (errors) => {
    console.error('Validation errors:', errors);
  }
});
```

### Server Endpoint (Python/FastAPI example)
```python
from fastapi import UploadFile, File
from typing import List

@app.post("/files/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({"name": file.filename, "size": len(content)})
    return HTMLResponse(f'<div class="greeble-drop-zone__result--success">Uploaded {len(results)} files</div>')
```

## Variants

### Compact
Add `greeble-drop-zone--compact` class for a smaller, horizontal layout.

```html
<div class="greeble-drop-zone greeble-drop-zone--compact" ...>
```
