# Step Progress Component

- **Purpose:** Progress indicator for multi-step workflows/pipelines. Shows step status, timing, and completion state.
- **Inputs:** Array of steps with titles; programmatic control via JavaScript API.
- **Outputs:** Step completion events with timing data.
- **Dependencies:** None required.
- **Events:**
  - `greeble:progress:stepstart` - Step started
  - `greeble:progress:stepcomplete` - Step completed with time
  - `greeble:progress:steperror` - Step failed with error
  - `greeble:progress:complete` - All steps completed
- **Accessibility:** Semantic list structure, status conveyed via text.

## Usage

### Basic HTML
```html
<div class="greeble-step-progress" id="step-progress" data-greeble-step-progress>
  <div class="greeble-step-progress__steps" id="step-progress-steps">
    <!-- Steps rendered dynamically -->
  </div>
  <div class="greeble-step-progress__total" id="step-progress-total">
    Total: <span id="step-progress-total-time">0ms</span>
  </div>
</div>
```

### JavaScript Initialization
```javascript
const progress = new GreebleStepProgress('#step-progress', {
  steps: [
    { id: 'read', title: 'Reading file' },
    { id: 'process', title: 'Processing data' },
    { id: 'save', title: 'Saving results' }
  ],
  onStepComplete: (step, time, index) => {
    console.log(`${step.title} completed in ${time}ms`);
  },
  onComplete: (steps, totalTime) => {
    console.log(`All done in ${totalTime}ms`);
  }
});

// Start the progress
progress.start();

// Manually advance steps
progress.nextStep();

// Complete current step with custom time
progress.completeStep(0, 150);

// Mark step as error
progress.errorStep(1, 'Connection failed');

// Skip a step
progress.skipStep(2);

// Reset all steps
progress.reset();
```

### Server-Side Updates (HTMX)

Use out-of-band swaps to update individual steps:

```python
@app.post("/pipeline/step/{step_id}")
async def update_step(step_id: str, status: str, time: int = None):
    return HTMLResponse(f'''
        <div 
            class="greeble-step-progress__step greeble-step-progress__step--{status}"
            id="{step_id}"
            hx-swap-oob="true"
        >
            <!-- step content -->
        </div>
    ''')
```

## Step Statuses

- **pending** - Not yet started (gray, numbered)
- **active** - Currently running (blue, spinner)
- **completed** - Successfully finished (green, checkmark)
- **error** - Failed (red, X mark)
- **skipped** - Intentionally skipped (gray, dimmed)

## Variants

### Compact
```html
<div class="greeble-step-progress greeble-step-progress--compact">
```

### Horizontal
```html
<div class="greeble-step-progress greeble-step-progress--horizontal">
```
