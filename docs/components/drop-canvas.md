# Drop Canvas

Drop target for building pipelines and workflows from draggable cards.

## Usage

```html
<div data-greeble-drop-canvas>
  <!-- Steps render here -->
</div>
```

## JavaScript API

```javascript
const canvas = new GreebleDropCanvas('#drop-canvas', {
  onStepAdded: (step, steps) => { /* handle step added */ },
  onStepRemoved: (step, steps) => { /* handle step removed */ },
  onRun: (steps) => { /* execute pipeline */ }
});
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `onStepAdded` | `function` | `null` | Callback when step is added |
| `onStepRemoved` | `function` | `null` | Callback when step is removed |
| `onRun` | `function` | `null` | Callback to execute the pipeline |
| `validateTypes` | `boolean` | `true` | Validate input/output type compatibility |

## Type Validation

The canvas validates that each step's output type is compatible with the next step's input type.
