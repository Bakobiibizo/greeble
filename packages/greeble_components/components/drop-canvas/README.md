# Drop Canvas Component

- **Purpose:** Drop target for building pipelines/workflows from draggable cards. Validates type compatibility between steps.
- **Inputs:** Draggable cards dropped from a card palette; step reordering and removal.
- **Outputs:** Ordered list of steps; run event with pipeline data.
- **Dependencies:** Works with draggable-card component; HTMX optional for run action.
- **Endpoints:** `POST /pipeline/run` (configurable via `hx-post`).
- **Security:** See [Security Considerations](#security-considerations) below.
- **Events:**
  - `greeble:canvas:stepadded` - Step added to pipeline
  - `greeble:canvas:stepremoved` - Step removed from pipeline
  - `greeble:canvas:stepschanged` - Steps reordered
  - `greeble:canvas:cleared` - All steps cleared
  - `greeble:canvas:run` - Pipeline run triggered
- **Accessibility:** Keyboard accessible step controls, ARIA live regions.

## Usage

### Basic HTML
```html
<div class="greeble-drop-canvas" id="drop-canvas" data-greeble-drop-canvas>
  <div class="greeble-drop-canvas__header">
    <h3 class="greeble-drop-canvas__title">Pipeline</h3>
    <div class="greeble-drop-canvas__actions">
      <button type="button" id="drop-canvas-clear">Clear</button>
    </div>
  </div>
  <div class="greeble-drop-canvas__zone" id="drop-canvas-zone">
    <div class="greeble-drop-canvas__empty" id="drop-canvas-empty">
      Drag items here
    </div>
    <div class="greeble-drop-canvas__steps" id="drop-canvas-steps"></div>
  </div>
  <div class="greeble-drop-canvas__footer">
    <button type="button" id="drop-canvas-run" disabled>Run Pipeline</button>
  </div>
</div>
```

### JavaScript Initialization
```javascript
const canvas = new GreebleDropCanvas('#drop-canvas', {
  validateTypes: true,
  onStepAdded: (step, steps) => {
    console.log('Added:', step);
    console.log('All steps:', steps);
  },
  onRun: (steps) => {
    console.log('Running pipeline with steps:', steps);
    // Send to server
    fetch('/api/pipeline/run', {
      method: 'POST',
      body: JSON.stringify({ steps })
    });
  },
  onTypeError: (output, input, name) => {
    console.error(`Type mismatch: ${output} -> ${input}`);
  }
});

// Get current steps
const steps = canvas.getSteps();

// Set steps programmatically
canvas.setSteps([
  { id: 'file-reader', title: 'File Reader', accepts: ['file'], produces: 'text' },
  { id: 'llm', title: 'LLM', accepts: ['text'], produces: 'text' }
]);

// Clear all steps
canvas.clear();
```

### With Card Palette
```javascript
// Initialize palette with compatibility highlighting
const palette = new GreebleCardPalette('#palette', {
  onCardDragStart: (data) => {
    // Palette will auto-highlight compatible cards
  }
});

// Initialize canvas
const canvas = new GreebleDropCanvas('#canvas');

// Listen for step changes to update palette highlights
document.addEventListener('greeble:canvas:stepadded', (e) => {
  const lastStep = e.detail.steps[e.detail.steps.length - 1];
  palette.highlightCompatible(lastStep.produces);
});
```

## Type Compatibility

The canvas validates that each step's output type is compatible with the next step's input type:

| Output | Compatible Inputs |
|--------|-------------------|
| text | text, json, docs |
| json | json, text |
| docs | docs |
| image | image |
| audio | audio |
| video | video |
| any | (all types) |

## Security Considerations

When using this component with HTMX, ensure your backend implements proper security measures:

### CSRF Protection

Add a CSRF token to the run button:

```html
<button
  id="drop-canvas-run"
  hx-post="/pipeline/run"
  hx-headers='{"X-CSRF-Token": "{{ csrf_token }}"}'
>
  Run Pipeline
</button>
```

### Input Validation

The component sanitizes step data before rendering, but your backend should also:

1. **Validate step IDs** - Ensure they match expected patterns
2. **Sanitize step titles** - Escape HTML/script content
3. **Verify step types** - Check against a whitelist of allowed types
4. **Authenticate requests** - Verify user has permission to run pipelines

### Example Backend (Python/FastAPI)

```python
from fastapi import Depends, HTTPException
from fastapi.security import CSRFProtect

@app.post("/pipeline/run")
async def run_pipeline(
    steps: list[dict],
    csrf_token: str = Depends(verify_csrf_token),
    user: User = Depends(get_current_user)
):
    # Validate each step
    for step in steps:
        if not is_valid_step_id(step.get('id')):
            raise HTTPException(400, "Invalid step ID")
        if not is_allowed_type(step.get('produces')):
            raise HTTPException(400, "Invalid step type")
    
    # Process pipeline...
```
