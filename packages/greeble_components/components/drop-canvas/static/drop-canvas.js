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

    // Render steps
    this.stepsContainer.innerHTML = this.steps.map((step, index) => {
      const inputType = this.getTypeLabel(step.accepts);
      const outputType = this.getTypeLabel(step.produces);
      
      return `
        <div class="greeble-drop-canvas__step" data-step-id="${step.stepId}" data-step-index="${index}">
          <div class="greeble-drop-canvas__step-header">
            <span class="greeble-drop-canvas__step-number">${index + 1}</span>
            <span class="greeble-drop-canvas__step-title">${step.title || step.id}</span>
            <div class="greeble-drop-canvas__step-actions">
              <button type="button" class="greeble-drop-canvas__step-move" data-direction="up" aria-label="Move up" ${index === 0 ? 'disabled' : ''}>↑</button>
              <button type="button" class="greeble-drop-canvas__step-move" data-direction="down" aria-label="Move down" ${index === this.steps.length - 1 ? 'disabled' : ''}>↓</button>
              <button type="button" class="greeble-drop-canvas__step-remove" aria-label="Remove step">✕</button>
            </div>
          </div>
          <div class="greeble-drop-canvas__step-types">
            <span class="greeble-type-badge greeble-type-badge--${inputType}">${inputType}</span>
            <span class="greeble-drop-canvas__step-arrow">→</span>
            <span class="greeble-type-badge greeble-type-badge--${outputType}">${outputType}</span>
          </div>
        </div>
        ${index < this.steps.length - 1 ? `
          <div class="greeble-drop-canvas__connector">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <polyline points="19 12 12 19 5 12"/>
            </svg>
          </div>
        ` : ''}
      `;
    }).join('');

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
    error.innerHTML = `
      <div class="greeble-drop-canvas__error-title">Type Mismatch</div>
      <div class="greeble-drop-canvas__error-message">
        Cannot connect <strong>${outputType}</strong> to <strong>${inputType}</strong>
        <br>${stepName} expects ${inputType}
      </div>
    `;
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
