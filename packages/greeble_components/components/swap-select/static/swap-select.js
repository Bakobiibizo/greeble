/**
 * Greeble Swap Select
 * Paired select dropdowns with swap functionality.
 * 
 * Usage:
 *   const swapSelect = new GreebleSwapSelect('#swap-select', {
 *     onSwap: (leftValue, rightValue) => { ... },
 *     onChange: (side, value) => { ... }
 *   });
 */
class GreebleSwapSelect {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;
    
    if (!this.container) {
      console.error('GreebleSwapSelect: Container not found');
      return;
    }

    this.options = {
      leftId: 'swap-select-left',
      rightId: 'swap-select-right',
      buttonId: 'swap-select-button',
      preventSameValue: false, // Prevent both selects from having same value
      onSwap: null,
      onChange: null,
      ...options
    };

    this.swapped = false;
    this.init();
  }

  init() {
    this.leftSelect = this.container.querySelector(`#${this.options.leftId}`);
    this.rightSelect = this.container.querySelector(`#${this.options.rightId}`);
    this.swapButton = this.container.querySelector(`#${this.options.buttonId}`);

    this.bindEvents();
  }

  bindEvents() {
    // Swap button click
    if (this.swapButton) {
      this.swapButton.addEventListener('click', () => this.swap());
    }

    // Select change events
    if (this.leftSelect) {
      this.leftSelect.addEventListener('change', (e) => {
        this.handleChange('left', e.target.value);
      });
    }

    if (this.rightSelect) {
      this.rightSelect.addEventListener('change', (e) => {
        this.handleChange('right', e.target.value);
      });
    }

    // Keyboard shortcut (Ctrl/Cmd + Shift + S to swap)
    this.container.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        this.swap();
      }
    });
  }

  swap() {
    if (!this.leftSelect || !this.rightSelect) return;

    const leftValue = this.leftSelect.value;
    const rightValue = this.rightSelect.value;

    // Swap values
    this.leftSelect.value = rightValue;
    this.rightSelect.value = leftValue;

    // Toggle swapped state for visual feedback
    this.swapped = !this.swapped;
    this.swapButton?.classList.toggle('greeble-swap-select__swap--swapped', this.swapped);

    // Callbacks
    if (this.options.onSwap) {
      this.options.onSwap(this.leftSelect.value, this.rightSelect.value);
    }

    // Dispatch event
    this.container.dispatchEvent(new CustomEvent('greeble:swap:swapped', {
      bubbles: true,
      detail: {
        left: this.leftSelect.value,
        right: this.rightSelect.value
      }
    }));

    // Trigger change events on selects for HTMX
    this.leftSelect.dispatchEvent(new Event('change', { bubbles: true }));
    this.rightSelect.dispatchEvent(new Event('change', { bubbles: true }));
  }

  handleChange(side, value) {
    // Prevent same value if configured
    if (this.options.preventSameValue) {
      const otherSelect = side === 'left' ? this.rightSelect : this.leftSelect;
      if (otherSelect && otherSelect.value === value) {
        // Find a different value for the other select
        const options = Array.from(otherSelect.options);
        const differentOption = options.find(opt => opt.value !== value && opt.value !== '');
        if (differentOption) {
          otherSelect.value = differentOption.value;
        }
      }
    }

    if (this.options.onChange) {
      this.options.onChange(side, value);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:swap:change', {
      bubbles: true,
      detail: {
        side,
        value,
        left: this.leftSelect?.value,
        right: this.rightSelect?.value
      }
    }));
  }

  // Public API
  getValues() {
    return {
      left: this.leftSelect?.value,
      right: this.rightSelect?.value
    };
  }

  setValues(left, right) {
    if (this.leftSelect && left !== undefined) {
      this.leftSelect.value = left;
    }
    if (this.rightSelect && right !== undefined) {
      this.rightSelect.value = right;
    }
  }

  setLeftValue(value) {
    if (this.leftSelect) {
      this.leftSelect.value = value;
      this.handleChange('left', value);
    }
  }

  setRightValue(value) {
    if (this.rightSelect) {
      this.rightSelect.value = value;
      this.handleChange('right', value);
    }
  }

  // Populate options programmatically
  setOptions(options, side = 'both') {
    const createOptions = (selectEl) => {
      selectEl.innerHTML = '';
      options.forEach(opt => {
        const optionEl = document.createElement('option');
        optionEl.value = typeof opt === 'object' ? opt.value : opt;
        optionEl.textContent = typeof opt === 'object' ? opt.label : opt;
        if (typeof opt === 'object' && opt.selected) {
          optionEl.selected = true;
        }
        selectEl.appendChild(optionEl);
      });
    };

    if (side === 'left' || side === 'both') {
      if (this.leftSelect) createOptions(this.leftSelect);
    }
    if (side === 'right' || side === 'both') {
      if (this.rightSelect) createOptions(this.rightSelect);
    }
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-swap-select]').forEach(el => {
    new GreebleSwapSelect(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleSwapSelect;
}
