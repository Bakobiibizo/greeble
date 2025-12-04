/**
 * Greeble Drop Canvas
 * Drop target for building pipelines/workflows from draggable cards.
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
      onStepAdded: null,
      onStepRemoved: null,
      onStepsChanged: null,
      onRun: null,
      onTypeError: null,
      ...options
    };

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
    this.stepsContainer.innerHTML = '';
    
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

  getTypeLabel(types) {
    if (!types) return 'any';
    const typeArray = Array.isArray(types) ? types : [types];
    if (typeArray.length === 0) return 'any';

    const first = typeArray[0];
    
    if (first.includes('audio/')) return 'audio';
    if (first.includes('video/')) return 'video';
    if (first.includes('image/')) return 'image';
    if (first.includes('json')) return 'json';
    if (first.includes('markdown')) return 'markdown';
    if (typeArray.length > 3 || first === '*/*') return 'docs';
    
    return 'text';
  }

  isTypeCompatible(outputType, inputType) {
    if (inputType === 'any' || outputType === 'any') return true;
    if (outputType === inputType) return true;
    
    // JSON is compatible with text
    if (outputType === 'json' && inputType === 'text') return true;
    if (outputType === 'text' && inputType === 'json') return true;
    
    // Docs accepts most text-based types
    if (inputType === 'docs' && ['text', 'json', 'markdown'].includes(outputType)) return true;
    
    return false;
  }

  showTypeError(outputType, inputType, stepName) {
    const error = document.createElement('div');
    error.className = 'greeble-drop-canvas__error';

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

    document.body.appendChild(error);

    if (this.options.onTypeError) {
      this.options.onTypeError(outputType, inputType, stepName);
    }

    setTimeout(() => error.remove(), 3000);
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
