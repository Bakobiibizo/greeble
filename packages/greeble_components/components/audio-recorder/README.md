# Audio Recorder Component

- **Purpose:** Microphone recording button with MediaRecorder API, preview playback, and HTMX upload support.
- **Inputs:** Click to start/stop recording; optional max duration and mime type configuration.
- **Outputs:** Audio blob for upload; preview with playback controls.
- **Dependencies:** HTMX (optional); MediaRecorder API (browser support required).
- **Endpoints:** `POST /audio/upload` (configurable via `hx-post`).
- **Events:** 
  - `greeble:audio:start` - Recording started
  - `greeble:audio:stop` - Recording stopped
  - `greeble:audio:complete` - Recording complete with blob
  - `greeble:audio:submit` - Submit button clicked
  - `greeble:audio:discard` - Recording discarded
  - `greeble:audio:error` - Error occurred
- **Accessibility:** `aria-label` on buttons, `aria-live` on status region.

## Usage

### Basic HTML
```html
<div class="greeble-audio-recorder" id="audio-recorder" data-greeble-audio-recorder>
  <!-- Component HTML from template -->
</div>
```

### JavaScript Initialization
```javascript
const recorder = new GreebleAudioRecorder('#audio-recorder', {
  mimeType: 'audio/webm',
  maxDuration: 300000, // 5 minutes
  onRecordingComplete: (blob) => {
    console.log('Recording complete:', blob);
  }
});
```

### Server Endpoint (Python/FastAPI example)
```python
@app.post("/audio/upload")
async def upload_audio(audio: UploadFile = File(...)):
    content = await audio.read()
    # Process audio...
    return HTMLResponse('<div class="greeble-audio-recorder__result--success">Uploaded!</div>')
```
