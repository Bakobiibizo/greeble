# Step Progress

Visual progress indicator for multi-step processes with timing.

## Usage

```html
<div data-greeble-step-progress>
  <!-- Steps render here -->
</div>
```

## JavaScript API

```javascript
const progress = new GreebleStepProgress('#step-progress', {
  steps: [
    { id: 'step-1', title: 'Initialize' },
    { id: 'step-2', title: 'Process' },
    { id: 'step-3', title: 'Complete' }
  ],
  onStepComplete: (step, time) => { /* handle completion */ }
});

// Control steps
progress.startStep('step-1');
progress.completeStep('step-1');
progress.failStep('step-2', 'Error message');
progress.reset();
```

## Step States

- `pending` - Not yet started
- `active` - Currently in progress
- `completed` - Successfully finished
- `failed` - Failed with error

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `steps` | `array` | `[]` | Step definitions |
| `onStepComplete` | `function` | `null` | Step completion callback |
