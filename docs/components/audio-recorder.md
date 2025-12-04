# Audio Recorder

Record audio directly in the browser with playback preview.

## Usage

```html
<div data-greeble-audio-recorder>
  <!-- Component renders here -->
</div>
```

## JavaScript API

```javascript
const recorder = new GreebleAudioRecorder('#my-recorder', {
  onRecordingComplete: (blob) => { /* handle audio blob */ }
});
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `onRecordingComplete` | `function` | `null` | Callback when recording finishes |
| `onError` | `function` | `null` | Callback for errors |

## Events

- `greeble:audio:start` - Recording started
- `greeble:audio:stop` - Recording stopped
- `greeble:audio:submit` - Audio submitted
