/**
 * Greeble Step Progress
 * Progress indicator for multi-step workflows/pipelines.
 * 
 * Usage:
 *   const progress = new GreebleStepProgress('#step-progress', {
 *     steps: [
 *       { id: 'step-1', title: 'Step 1' },
 *       { id: 'step-2', title: 'Step 2' }
 *     ],
 *     onStepComplete: (step, time) => { ... }
 *   });
 */
class GreebleStepProgress {
  // Helper to escape HTML for safe attribute values
  static escapeAttr(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string'
      ? document.querySelector(selector)
      : selector;

    if (!this.container) {
      console.error('GreebleStepProgress: Container not found');
      return;
    }

    this.options = {
      steps: [],
      showTotal: true,
      autoStart: false,
      onStepStart: null,
      onStepComplete: null,
      onStepError: null,
      onComplete: null,
      ...options
    };

    this.steps = [];
    this.currentStepIndex = -1;
    this.stepStartTime = null;
    this.totalStartTime = null;
    this.totalTime = 0;

    this.init();
  }

  init() {
    this.stepsContainer = this.container.querySelector('#step-progress-steps');
    this.totalContainer = this.container.querySelector('#step-progress-total');
    this.totalTimeEl = this.container.querySelector('#step-progress-total-time');

    if (this.options.steps.length > 0) {
      this.setSteps(this.options.steps);
    }

    if (this.options.autoStart) {
      this.start();
    }
  }

  setSteps(steps) {
    this.steps = steps.map((step, index) => ({
      id: step.id || `step-${index + 1}`,
      title: step.title || `Step ${index + 1}`,
      status: 'pending',
      time: null,
      ...step
    }));

    this.currentStepIndex = -1;
    this.totalTime = 0;
    this.render();
  }

  render() {
    if (!this.stepsContainer) return;

    // Clear existing content
    this.stepsContainer.innerHTML = '';

    this.steps.forEach((step, index) => {
      const safeStatus = GreebleStepProgress.escapeAttr(step.status);
      
      const stepEl = document.createElement('div');
      stepEl.className = `greeble-step-progress__step greeble-step-progress__step--${safeStatus}`;
      stepEl.dataset.step = index + 1;
      stepEl.id = step.id;

      // Indicator
      const indicator = document.createElement('div');
      indicator.className = 'greeble-step-progress__step-indicator';
      // renderIndicator returns static SVG, safe to use innerHTML
      indicator.innerHTML = this.renderIndicator(step, index);
      stepEl.appendChild(indicator);

      // Content
      const content = document.createElement('div');
      content.className = 'greeble-step-progress__step-content';

      const titleEl = document.createElement('span');
      titleEl.className = 'greeble-step-progress__step-title';
      titleEl.textContent = step.title;
      content.appendChild(titleEl);

      const timeEl = document.createElement('span');
      timeEl.className = 'greeble-step-progress__step-time';
      timeEl.textContent = this.getTimeDisplay(step);
      content.appendChild(timeEl);

      stepEl.appendChild(content);
      this.stepsContainer.appendChild(stepEl);
    });

    this.updateTotal();
  }

  renderIndicator(step, index) {
    switch (step.status) {
      case 'completed':
        return `<svg class="greeble-step-progress__step-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <polyline points="20 6 9 17 4 12"/>
        </svg>`;
      case 'active':
        return `<svg class="greeble-step-progress__step-spinner" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="60" stroke-linecap="round"/>
        </svg>`;
      case 'error':
        return `<svg class="greeble-step-progress__step-error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>`;
      default:
        return `<span class="greeble-step-progress__step-number">${index + 1}</span>`;
    }
  }

  getTimeDisplay(step) {
    switch (step.status) {
      case 'completed':
        return step.time !== null ? this.formatTime(step.time) : 'Done';
      case 'active':
        return 'Running...';
      case 'error':
        return step.error || 'Error';
      case 'skipped':
        return 'Skipped';
      default:
        return 'Pending';
    }
  }

  formatTime(ms) {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  }

  updateTotal() {
    if (!this.totalTimeEl) return;

    const completedTime = this.steps
      .filter(s => s.status === 'completed' && s.time !== null)
      .reduce((sum, s) => sum + s.time, 0);

    this.totalTimeEl.textContent = this.formatTime(completedTime);

    // Show/hide total based on completion
    if (this.totalContainer) {
      const hasCompleted = this.steps.some(s => s.status === 'completed');
      this.totalContainer.hidden = !hasCompleted || !this.options.showTotal;
    }
  }

  // Control methods
  start() {
    if (this.steps.length === 0) return;

    this.totalStartTime = Date.now();
    this.currentStepIndex = -1;
    
    // Reset all steps
    this.steps.forEach(step => {
      step.status = 'pending';
      step.time = null;
    });

    this.nextStep();
  }

  nextStep() {
    // Complete current step if active
    if (this.currentStepIndex >= 0 && this.steps[this.currentStepIndex]?.status === 'active') {
      this.completeStep(this.currentStepIndex);
    }

    this.currentStepIndex++;

    if (this.currentStepIndex >= this.steps.length) {
      this.complete();
      return;
    }

    this.startStep(this.currentStepIndex);
  }

  startStep(index) {
    if (index < 0 || index >= this.steps.length) return;

    const step = this.steps[index];
    step.status = 'active';
    this.stepStartTime = Date.now();

    this.render();

    if (this.options.onStepStart) {
      this.options.onStepStart(step, index);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:progress:stepstart', {
      bubbles: true,
      detail: { step, index }
    }));
  }

  completeStep(index, time = null) {
    if (index < 0 || index >= this.steps.length) return;

    const step = this.steps[index];
    step.status = 'completed';
    step.time = time !== null ? time : (Date.now() - this.stepStartTime);

    this.render();

    if (this.options.onStepComplete) {
      this.options.onStepComplete(step, step.time, index);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:progress:stepcomplete', {
      bubbles: true,
      detail: { step, time: step.time, index }
    }));
  }

  errorStep(index, error = 'Error') {
    if (index < 0 || index >= this.steps.length) return;

    const step = this.steps[index];
    step.status = 'error';
    step.error = error;
    step.time = Date.now() - this.stepStartTime;

    this.render();

    if (this.options.onStepError) {
      this.options.onStepError(step, error, index);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:progress:steperror', {
      bubbles: true,
      detail: { step, error, index }
    }));
  }

  skipStep(index) {
    if (index < 0 || index >= this.steps.length) return;

    const step = this.steps[index];
    step.status = 'skipped';

    this.render();
  }

  complete() {
    this.totalTime = Date.now() - this.totalStartTime;

    if (this.options.onComplete) {
      this.options.onComplete(this.steps, this.totalTime);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:progress:complete', {
      bubbles: true,
      detail: { steps: this.steps, totalTime: this.totalTime }
    }));
  }

  reset() {
    this.steps.forEach(step => {
      step.status = 'pending';
      step.time = null;
      step.error = null;
    });
    this.currentStepIndex = -1;
    this.totalTime = 0;
    this.render();
  }

  // Update a specific step by ID or index
  updateStep(idOrIndex, updates) {
    const index = typeof idOrIndex === 'number' 
      ? idOrIndex 
      : this.steps.findIndex(s => s.id === idOrIndex);

    if (index < 0 || index >= this.steps.length) return;

    Object.assign(this.steps[index], updates);
    this.render();
  }

  // Public getters
  getSteps() {
    return [...this.steps];
  }

  getCurrentStep() {
    return this.currentStepIndex >= 0 ? this.steps[this.currentStepIndex] : null;
  }

  getTotalTime() {
    return this.totalTime;
  }

  isComplete() {
    return this.steps.every(s => s.status === 'completed' || s.status === 'skipped');
  }

  hasError() {
    return this.steps.some(s => s.status === 'error');
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-step-progress]').forEach(el => {
    new GreebleStepProgress(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleStepProgress;
}
