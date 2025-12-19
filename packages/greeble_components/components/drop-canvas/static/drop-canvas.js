/**
 * Greeble Drop Canvas
 * Drop target for building pipelines/workflows from draggable cards.
 *
 * SECURITY NOTE: When using with HTMX, ensure your backend implements:
 * - CSRF protection on the /pipeline/run endpoint
 * - Input validation and sanitization of step data
 * - Proper authentication/authorization checks
 *
 * Usage:
 *   const canvas = new GreebleDropCanvas('#drop-canvas', {
 *     onStepAdded: (step, steps) => { ... },
 *     onStepRemoved: (step, steps) => { ... },
 *     onRun: (steps) => { ... }
 *   });
 */
class GreebleDropCanvas {
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
      console.error('GreebleDropCanvas: Container not found');
      return;
    }

    this.options = {
      dataTransferType: 'application/json',
      validateTypes: true,
      maxErrorToasts: 3,
      errorContainer: null, // If null, uses container; set to element or selector for custom placement
      onStepAdded: null,
      onStepRemoved: null,
      onStepsChanged: null,
      onRun: null,
      onTypeError: null,
      ...options
    };

    this.activeErrors = [];

    this.steps = [];
    this.init();
  }

  init() {
    this.zone = this.container.querySelector('#drop-canvas-zone');
    this.emptyState = this.container.querySelector('#drop-canvas-empty');
    this.stepsContainer = this.container.querySelector('#drop-canvas-steps');
    this.clearBtn = this.container.querySelector('#drop-canvas-clear');
    this.runBtn = this.container.querySelector('#drop-canvas-run');

    this.bindEvents();
  }

  bindEvents() {
    // Drop zone events
    if (this.zone) {
      this.zone.addEventListener('dragover', (e) => this.handleDragOver(e));
      this.zone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
      this.zone.addEventListener('drop', (e) => this.handleDrop(e));
    }

    // Clear button
    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', () => this.clear());
    }

    // Run button
    if (this.runBtn) {
      this.runBtn.addEventListener('click', () => this.run());
      
      // HTMX integration - add steps data to request
      this.runBtn.addEventListener('htmx:configRequest', (e) => {
        e.detail.parameters['steps'] = JSON.stringify(this.steps);
      });
    }

    // Listen for card drag events to highlight compatibility
    document.addEventListener('greeble:card:dragstart', (e) => {
      this.highlightDropZone(e.detail.data);
    });

    document.addEventListener('greeble:card:dragend', () => {
      this.clearHighlight();
    });
  }

  handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    this.zone.classList.add('greeble-drop-canvas__zone--dragover');
  }

  handleDragLeave(e) {
    // Only remove highlight if leaving the zone entirely
    if (!this.zone.contains(e.relatedTarget)) {
      this.zone.classList.remove('greeble-drop-canvas__zone--dragover');
    }
  }

  handleDrop(e) {
    e.preventDefault();
    this.zone.classList.remove('greeble-drop-canvas__zone--dragover');

    try {
      const data = JSON.parse(e.dataTransfer.getData(this.options.dataTransferType));
      this.addStep(data);
    } catch (err) {
      console.error('GreebleDropCanvas: Invalid drop data', err);
    }
  }

  addStep(data) {
    // Validate type compatibility
    if (this.options.validateTypes && this.steps.length > 0) {
      const lastStep = this.steps[this.steps.length - 1];
      const lastOutput = this.getTypeLabel(lastStep.produces);
      const newInput = this.getTypeLabel(data.accepts);

      if (!this.isTypeCompatible(lastOutput, newInput)) {
        this.showTypeError(lastOutput, newInput, data.title || data.id);
        return;
      }
    }

    const step = {
      ...data,
      stepId: `step-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };

    this.steps.push(step);
    this.render();

    if (this.options.onStepAdded) {
      this.options.onStepAdded(step, this.steps);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:canvas:stepadded', {
      bubbles: true,
      detail: { step, steps: this.steps }
    }));
  }

  removeStep(stepId) {
    const index = this.steps.findIndex(s => s.stepId === stepId);
    if (index === -1) return;

    const [removed] = this.steps.splice(index, 1);
    this.render();

    if (this.options.onStepRemoved) {
      this.options.onStepRemoved(removed, this.steps);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:canvas:stepremoved', {
      bubbles: true,
      detail: { step: removed, steps: this.steps }
    }));
  }

  moveStep(stepId, direction) {
    const index = this.steps.findIndex(s => s.stepId === stepId);
    if (index === -1) return;

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= this.steps.length) return;

    // Swap steps
    [this.steps[index], this.steps[newIndex]] = [this.steps[newIndex], this.steps[index]];
    this.render();

    if (this.options.onStepsChanged) {
      this.options.onStepsChanged(this.steps);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:canvas:stepschanged', {
      bubbles: true,
      detail: { steps: this.steps }
    }));
  }

  render() {
    if (!this.stepsContainer) return;

    const hasSteps = this.steps.length > 0;

    // Toggle empty state
    if (this.emptyState) {
      this.emptyState.hidden = hasSteps;
    }

    // Toggle zone styling
    this.zone?.classList.toggle('greeble-drop-canvas__zone--has-steps', hasSteps);

    // Enable/disable run button
    if (this.runBtn) {
      this.runBtn.disabled = !hasSteps;
    }

    // Render steps using safe DOM methods
    this.stepsContainer.replaceChildren();

    this.steps.forEach((step, index) => {
      const inputType = this.getTypeLabel(step.accepts);
      const outputType = this.getTypeLabel(step.produces);
      const safeInputType = GreebleDropCanvas.escapeAttr(inputType);
      const safeOutputType = GreebleDropCanvas.escapeAttr(outputType);

      const stepEl = document.createElement('div');
      stepEl.className = 'greeble-drop-canvas__step';
      stepEl.dataset.stepId = step.stepId;
      stepEl.dataset.stepIndex = index;

      // Header
      const header = document.createElement('div');
      header.className = 'greeble-drop-canvas__step-header';

      const stepNumber = document.createElement('span');
      stepNumber.className = 'greeble-drop-canvas__step-number';
      stepNumber.textContent = index + 1;
      header.appendChild(stepNumber);

      const stepTitle = document.createElement('span');
      stepTitle.className = 'greeble-drop-canvas__step-title';
      stepTitle.textContent = step.title || step.id;
      header.appendChild(stepTitle);

      const actions = document.createElement('div');
      actions.className = 'greeble-drop-canvas__step-actions';

      const upBtn = document.createElement('button');
      upBtn.type = 'button';
      upBtn.className = 'greeble-drop-canvas__step-move';
      upBtn.dataset.direction = 'up';
      upBtn.setAttribute('aria-label', 'Move up');
      upBtn.textContent = '↑';
      if (index === 0) upBtn.disabled = true;
      actions.appendChild(upBtn);

      const downBtn = document.createElement('button');
      downBtn.type = 'button';
      downBtn.className = 'greeble-drop-canvas__step-move';
      downBtn.dataset.direction = 'down';
      downBtn.setAttribute('aria-label', 'Move down');
      downBtn.textContent = '↓';
      if (index === this.steps.length - 1) downBtn.disabled = true;
      actions.appendChild(downBtn);

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'greeble-drop-canvas__step-remove';
      removeBtn.setAttribute('aria-label', 'Remove step');
      removeBtn.textContent = '✕';
      actions.appendChild(removeBtn);

      header.appendChild(actions);
      stepEl.appendChild(header);

      // Types
      const types = document.createElement('div');
      types.className = 'greeble-drop-canvas__step-types';

      const inputBadge = document.createElement('span');
      inputBadge.className = `greeble-type-badge greeble-type-badge--${safeInputType}`;
      inputBadge.textContent = inputType;
      types.appendChild(inputBadge);

      const arrow = document.createElement('span');
      arrow.className = 'greeble-drop-canvas__step-arrow';
      arrow.textContent = '→';
      types.appendChild(arrow);

      const outputBadge = document.createElement('span');
      outputBadge.className = `greeble-type-badge greeble-type-badge--${safeOutputType}`;
      outputBadge.textContent = outputType;
      types.appendChild(outputBadge);

      stepEl.appendChild(types);
      this.stepsContainer.appendChild(stepEl);

      // Add connector between steps
      if (index < this.steps.length - 1) {
        const connector = document.createElement('div');
        connector.className = 'greeble-drop-canvas__connector';
        connector.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/>
          <polyline points="19 12 12 19 5 12"/>
        </svg>`;
        this.stepsContainer.appendChild(connector);
      }
    });

    // Bind step action buttons
    this.stepsContainer.querySelectorAll('.greeble-drop-canvas__step-remove').forEach(btn => {
      btn.addEventListener('click', () => {
        const stepEl = btn.closest('.greeble-drop-canvas__step');
        this.removeStep(stepEl.dataset.stepId);
      });
    });

    this.stepsContainer.querySelectorAll('.greeble-drop-canvas__step-move').forEach(btn => {
      btn.addEventListener('click', () => {
        const stepEl = btn.closest('.greeble-drop-canvas__step');
        this.moveStep(stepEl.dataset.stepId, btn.dataset.direction);
      });
    });
  }

  clear() {
    this.steps = [];
    this.render();

    this.container.dispatchEvent(new CustomEvent('greeble:canvas:cleared', {
      bubbles: true
    }));
  }

  run() {
    if (this.steps.length === 0) return;

    if (this.options.onRun) {
      this.options.onRun(this.steps);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:canvas:run', {
      bubbles: true,
      detail: { steps: this.steps }
    }));
  }

  /**
   * Maps type strings to normalized type labels.
   * Uses a whitelist approach for security - unknown types default to 'text'.
   */
  getTypeLabel(types) {
    if (!types) return 'any';
    const typeArray = Array.isArray(types) ? types : [types];
    if (typeArray.length === 0) return 'any';

    const first = String(typeArray[0] || '').toLowerCase();
    
    // Whitelist of known MIME type patterns
    const typeMap = {
      'audio': /^audio\//,
      'video': /^video\//,
      'image': /^image\//,
      'json': /json/,
      'markdown': /markdown/,
      'docs': /^(application\/(pdf|msword|vnd\.))|text\/(html|xml)/
    };

    for (const [label, pattern] of Object.entries(typeMap)) {
      if (pattern.test(first)) return label;
    }

    // Wildcard or many types indicates docs
    if (first === '*/*' || typeArray.length > 3) return 'docs';
    
    return 'text';
  }

  /**
   * Checks if an output type is compatible with an input type.
   *
   * Compatibility rules:
   * - 'any' is compatible with everything (wildcard)
   * - Same types are always compatible
   * - JSON <-> text: JSON can be stringified to text, text can often be parsed as JSON
   * - docs accepts text-based types: documents can contain text, JSON, or markdown
   *
   * @param {string} outputType - The type being produced
   * @param {string} inputType - The type being accepted
   * @returns {boolean} Whether the types are compatible
   */
  isTypeCompatible(outputType, inputType) {
    if (inputType === 'any' || outputType === 'any') return true;
    if (outputType === inputType) return true;
    
    // JSON <-> text compatibility:
    // JSON can be serialized to text (JSON.stringify), and text can often be parsed as JSON.
    // This allows flexible data handling in pipelines where format conversion is implicit.
    if (outputType === 'json' && inputType === 'text') return true;
    if (outputType === 'text' && inputType === 'json') return true;
    
    // Docs accepts most text-based types since documents can contain various text formats
    if (inputType === 'docs' && ['text', 'json', 'markdown'].includes(outputType)) return true;
    
    return false;
  }

  /**
   * Shows a type error toast within a controlled container.
   * Limits the number of simultaneous error toasts to prevent DoS.
   */
  showTypeError(outputType, inputType, stepName) {
    // Limit number of active error toasts
    if (this.activeErrors.length >= this.options.maxErrorToasts) {
      const oldest = this.activeErrors.shift();
      oldest?.remove();
    }

    const error = document.createElement('div');
    error.className = 'greeble-drop-canvas__error';
    error.setAttribute('role', 'alert');

    const title = document.createElement('div');
    title.className = 'greeble-drop-canvas__error-title';
    title.textContent = 'Type Mismatch';
    error.appendChild(title);

    const message = document.createElement('div');
    message.className = 'greeble-drop-canvas__error-message';
    
    const text1 = document.createTextNode('Cannot connect ');
    const strong1 = document.createElement('strong');
    strong1.textContent = outputType;
    const text2 = document.createTextNode(' to ');
    const strong2 = document.createElement('strong');
    strong2.textContent = inputType;
    const br = document.createElement('br');
    const text3 = document.createTextNode(`${stepName} expects ${inputType}`);
    
    message.appendChild(text1);
    message.appendChild(strong1);
    message.appendChild(text2);
    message.appendChild(strong2);
    message.appendChild(br);
    message.appendChild(text3);
    error.appendChild(message);

    // Append to specified container or fallback to component container
    const errorContainer = this.options.errorContainer
      ? (typeof this.options.errorContainer === 'string'
          ? document.querySelector(this.options.errorContainer)
          : this.options.errorContainer)
      : this.container;

    (errorContainer || this.container).appendChild(error);
    this.activeErrors.push(error);

    if (this.options.onTypeError) {
      this.options.onTypeError(outputType, inputType, stepName);
    }

    setTimeout(() => {
      const idx = this.activeErrors.indexOf(error);
      if (idx > -1) this.activeErrors.splice(idx, 1);
      error.remove();
    }, 3000);
  }

  highlightDropZone(cardData) {
    if (this.steps.length === 0) {
      this.zone?.classList.add('greeble-drop-canvas__zone--dragover');
      return;
    }

    const lastStep = this.steps[this.steps.length - 1];
    const lastOutput = this.getTypeLabel(lastStep.produces);
    const newInput = this.getTypeLabel(cardData.accepts);

    if (this.isTypeCompatible(lastOutput, newInput)) {
      this.zone?.classList.add('greeble-drop-canvas__zone--dragover');
    }
  }

  clearHighlight() {
    this.zone?.classList.remove('greeble-drop-canvas__zone--dragover');
  }

  // Public API
  getSteps() {
    return [...this.steps];
  }

  setSteps(steps) {
    this.steps = steps.map(step => ({
      ...step,
      stepId: step.stepId || `step-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    }));
    this.render();
  }

  getStepData() {
    return this.steps.map(({ stepId, ...data }) => data);
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-drop-canvas]').forEach(el => {
    new GreebleDropCanvas(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleDropCanvas;
}
