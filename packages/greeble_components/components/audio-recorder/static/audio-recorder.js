/**
 * Greeble Audio Recorder
 * Generic audio recording component using MediaRecorder API.
 * 
 * Usage:
 *   const recorder = new GreebleAudioRecorder('#audio-recorder', {
 *     onRecordingComplete: (blob) => { ... },
 *     mimeType: 'audio/webm',
 *     maxDuration: 300000 // 5 minutes
 *   });
 */
class GreebleAudioRecorder {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;
    
    if (!this.container) {
      console.error('GreebleAudioRecorder: Container not found');
      return;
    }

    this.options = {
      mimeType: 'audio/webm',
      maxDuration: 300000, // 5 minutes default
      onRecordingStart: null,
      onRecordingStop: null,
      onRecordingComplete: null,
      onError: null,
      ...options
    };

    this.mediaRecorder = null;
    this.audioChunks = [];
    this.audioBlob = null;
    this.stream = null;
    this.startTime = null;
    this.timerInterval = null;

    this.init();
  }

  init() {
    this.startBtn = this.container.querySelector('#audio-recorder-start');
    this.stopBtn = this.container.querySelector('#audio-recorder-stop');
    this.status = this.container.querySelector('#audio-recorder-status');
    this.preview = this.container.querySelector('#audio-recorder-preview');
    this.playback = this.container.querySelector('#audio-recorder-playback');
    this.discardBtn = this.container.querySelector('#audio-recorder-discard');
    this.submitBtn = this.container.querySelector('#audio-recorder-submit');

    if (this.startBtn) {
      this.startBtn.addEventListener('click', () => this.startRecording());
    }
    if (this.stopBtn) {
      this.stopBtn.addEventListener('click', () => this.stopRecording());
    }
    if (this.discardBtn) {
      this.discardBtn.addEventListener('click', () => this.discard());
    }
    if (this.submitBtn) {
      this.submitBtn.addEventListener('click', (e) => this.prepareSubmit(e));
    }
  }

  async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Determine best mime type
      const mimeType = MediaRecorder.isTypeSupported(this.options.mimeType)
        ? this.options.mimeType
        : 'audio/webm';
      
      this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = () => this.handleRecordingComplete();

      this.mediaRecorder.start();
      this.startTime = Date.now();
      this.updateUI('recording');
      this.startTimer();

      // Auto-stop after max duration
      setTimeout(() => {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
          this.stopRecording();
        }
      }, this.options.maxDuration);

      if (this.options.onRecordingStart) {
        this.options.onRecordingStart();
      }

      this.container.dispatchEvent(new CustomEvent('greeble:audio:start', {
        bubbles: true
      }));

    } catch (error) {
      console.error('Error accessing microphone:', error);
      this.handleError(error);
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
      this.mediaRecorder.stop();
      this.stream.getTracks().forEach(track => track.stop());
      this.stopTimer();
      
      if (this.options.onRecordingStop) {
        this.options.onRecordingStop();
      }

      this.container.dispatchEvent(new CustomEvent('greeble:audio:stop', {
        bubbles: true
      }));
    }
  }

  handleRecordingComplete() {
    this.audioBlob = new Blob(this.audioChunks, { type: this.options.mimeType });
    const audioURL = URL.createObjectURL(this.audioBlob);
    
    if (this.playback) {
      this.playback.src = audioURL;
    }
    
    this.updateUI('preview');

    if (this.options.onRecordingComplete) {
      this.options.onRecordingComplete(this.audioBlob);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:audio:complete', {
      bubbles: true,
      detail: { blob: this.audioBlob, url: audioURL }
    }));
  }

  prepareSubmit(event) {
    if (!this.audioBlob) return;

    // Create FormData with the audio blob
    const formData = new FormData();
    formData.append('audio', this.audioBlob, 'recording.webm');

    // If using HTMX, set the values
    if (window.htmx && this.submitBtn) {
      // Store blob for HTMX to pick up
      this.submitBtn._greebleAudioBlob = this.audioBlob;
      
      // Use htmx:configRequest to add the file
      this.submitBtn.addEventListener('htmx:configRequest', (e) => {
        e.detail.parameters['audio'] = this.audioBlob;
      }, { once: true });
    }

    this.container.dispatchEvent(new CustomEvent('greeble:audio:submit', {
      bubbles: true,
      detail: { blob: this.audioBlob, formData }
    }));
  }

  discard() {
    this.audioBlob = null;
    this.audioChunks = [];
    if (this.playback) {
      this.playback.src = '';
    }
    this.updateUI('idle');

    this.container.dispatchEvent(new CustomEvent('greeble:audio:discard', {
      bubbles: true
    }));
  }

  startTimer() {
    this.timerInterval = setInterval(() => {
      const elapsed = Date.now() - this.startTime;
      const seconds = Math.floor(elapsed / 1000);
      const minutes = Math.floor(seconds / 60);
      const displaySeconds = seconds % 60;
      
      if (this.status) {
        this.status.textContent = `Recording ${minutes}:${displaySeconds.toString().padStart(2, '0')}`;
        this.status.classList.add('greeble-audio-recorder__status--recording');
      }
    }, 100);
  }

  stopTimer() {
    if (this.timerInterval) {
      clearInterval(this.timerInterval);
      this.timerInterval = null;
    }
  }

  updateUI(state) {
    switch (state) {
      case 'recording':
        if (this.startBtn) this.startBtn.hidden = true;
        if (this.stopBtn) this.stopBtn.hidden = false;
        if (this.preview) this.preview.hidden = true;
        break;
      case 'preview':
        if (this.startBtn) this.startBtn.hidden = false;
        if (this.stopBtn) this.stopBtn.hidden = true;
        if (this.preview) this.preview.hidden = false;
        if (this.status) {
          this.status.textContent = 'Recording complete';
          this.status.classList.remove('greeble-audio-recorder__status--recording');
        }
        break;
      case 'idle':
      default:
        if (this.startBtn) this.startBtn.hidden = false;
        if (this.stopBtn) this.stopBtn.hidden = true;
        if (this.preview) this.preview.hidden = true;
        if (this.status) {
          this.status.textContent = '';
          this.status.classList.remove('greeble-audio-recorder__status--recording');
        }
        break;
    }
  }

  handleError(error) {
    let message = 'Error accessing microphone';
    
    if (error.name === 'NotAllowedError') {
      message = 'Microphone access denied. Please allow microphone access.';
    } else if (error.name === 'NotFoundError') {
      message = 'No microphone found. Please connect a microphone.';
    }

    if (this.status) {
      this.status.textContent = message;
    }

    if (this.options.onError) {
      this.options.onError(error);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:audio:error', {
      bubbles: true,
      detail: { error, message }
    }));
  }

  // Public method to get the recorded blob
  getBlob() {
    return this.audioBlob;
  }

  // Public method to get blob as base64
  async getBlobAsBase64() {
    if (!this.audioBlob) return null;
    
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.readAsDataURL(this.audioBlob);
    });
  }
}

// Auto-initialize if data attribute present
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-audio-recorder]').forEach(el => {
    new GreebleAudioRecorder(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleAudioRecorder;
}
