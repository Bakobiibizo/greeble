/**
 * Greeble Draggable Card
 * Draggable card component for building pipeline/workflow interfaces.
 * 
 * Usage:
 *   const card = new GreebleDraggableCard('.greeble-draggable-card', {
 *     onDragStart: (data) => { ... },
 *     onDragEnd: (data) => { ... }
 *   });
 */
class GreebleDraggableCard {
  constructor(selector, options = {}) {
    this.elements = typeof selector === 'string'
      ? document.querySelectorAll(selector)
      : [selector];

    this.options = {
      onDragStart: null,
      onDragEnd: null,
      dataTransferType: 'application/json',
      ...options
    };

    this.init();
  }

  init() {
    this.elements.forEach(el => this.bindCard(el));
  }

  bindCard(card) {
    card.addEventListener('dragstart', (e) => this.handleDragStart(e, card));
    card.addEventListener('dragend', (e) => this.handleDragEnd(e, card));
  }

  handleDragStart(e, card) {
    const data = this.getCardData(card);
    
    // Set drag data
    e.dataTransfer.setData(this.options.dataTransferType, JSON.stringify(data));
    e.dataTransfer.effectAllowed = 'copy';

    // Visual feedback
    card.classList.add('greeble-draggable-card--dragging');

    // Callback
    if (this.options.onDragStart) {
      this.options.onDragStart(data, card, e);
    }

    // Dispatch event
    card.dispatchEvent(new CustomEvent('greeble:card:dragstart', {
      bubbles: true,
      detail: { data, card }
    }));
  }

  handleDragEnd(e, card) {
    const data = this.getCardData(card);
    
    // Remove visual feedback
    card.classList.remove('greeble-draggable-card--dragging');

    // Callback
    if (this.options.onDragEnd) {
      this.options.onDragEnd(data, card, e);
    }

    // Dispatch event
    card.dispatchEvent(new CustomEvent('greeble:card:dragend', {
      bubbles: true,
      detail: { data, card }
    }));
  }

  getCardData(card) {
    return {
      id: card.dataset.id,
      category: card.dataset.category,
      accepts: card.dataset.accepts?.split(',') || [],
      produces: card.dataset.produces,
      title: card.querySelector('.greeble-draggable-card__title')?.textContent,
      description: card.querySelector('.greeble-draggable-card__description')?.textContent
    };
  }

  // Helper to escape HTML for safe attribute values
  static escapeAttr(str) {
    if (!str) return '';
    return String(str).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }

  // Static method to create card from data
  static createCard(data, options = {}) {
    const card = document.createElement('div');
    const safeCategory = GreebleDraggableCard.escapeAttr(data.category) || 'default';
    card.className = `greeble-draggable-card greeble-draggable-card--${safeCategory}`;
    card.draggable = true;
    card.dataset.id = data.id;
    card.dataset.category = data.category || 'default';
    card.dataset.accepts = Array.isArray(data.accepts) ? data.accepts.join(',') : data.accepts;
    card.dataset.produces = data.produces;

    // Build card using safe DOM methods
    const header = document.createElement('div');
    header.className = 'greeble-draggable-card__header';

    const icon = document.createElement('span');
    icon.className = 'greeble-draggable-card__icon';
    icon.textContent = data.icon || '📦';
    header.appendChild(icon);

    const title = document.createElement('span');
    title.className = 'greeble-draggable-card__title';
    title.textContent = data.title || data.id;
    header.appendChild(title);

    card.appendChild(header);

    const types = document.createElement('div');
    types.className = 'greeble-draggable-card__types';

    const inputType = GreebleDraggableCard.escapeAttr(data.inputType) || 'text';
    const inputBadge = document.createElement('span');
    inputBadge.className = `greeble-type-badge greeble-type-badge--${inputType}`;
    inputBadge.textContent = data.inputLabel || data.accepts;
    types.appendChild(inputBadge);

    const arrow = document.createElement('span');
    arrow.className = 'greeble-draggable-card__arrow';
    arrow.textContent = '→';
    types.appendChild(arrow);

    const outputType = GreebleDraggableCard.escapeAttr(data.outputType) || 'text';
    const outputBadge = document.createElement('span');
    outputBadge.className = `greeble-type-badge greeble-type-badge--${outputType}`;
    outputBadge.textContent = data.outputLabel || data.produces;
    types.appendChild(outputBadge);

    card.appendChild(types);

    if (data.description) {
      const desc = document.createElement('p');
      desc.className = 'greeble-draggable-card__description';
      desc.textContent = data.description;
      card.appendChild(desc);
    }

    if (options.container) {
      options.container.appendChild(card);
    }

    return card;
  }
}

/**
 * Greeble Card Palette
 * Container for organizing draggable cards by category.
 */
class GreebleCardPalette {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string'
      ? document.querySelector(selector)
      : selector;

    if (!this.container) {
      console.error('GreebleCardPalette: Container not found');
      return;
    }

    this.options = {
      cards: [],
      categories: ['ingestor', 'generator', 'formatter', 'processor', 'tool'],
      categoryLabels: {
        ingestor: 'Ingestors',
        generator: 'Generators',
        formatter: 'Formatters',
        processor: 'Processors',
        tool: 'Tools'
      },
      onCardDragStart: null,
      ...options
    };

    this.cardInstances = [];
    this.init();
  }

  init() {
    // Initialize existing cards
    const existingCards = this.container.querySelectorAll('[data-greeble-draggable]');
    existingCards.forEach(card => {
      const instance = new GreebleDraggableCard(card, {
        onDragStart: this.options.onCardDragStart
      });
      this.cardInstances.push(instance);
    });

    // Render provided cards
    if (this.options.cards.length > 0) {
      this.renderCards(this.options.cards);
    }
  }

  renderCards(cards) {
    // Group cards by category
    const grouped = {};
    cards.forEach(card => {
      const category = card.category || 'default';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(card);
    });

    // Render each category
    this.options.categories.forEach(category => {
      if (!grouped[category]) return;

      let categoryEl = this.container.querySelector(`[data-category="${category}"]`);
      
      if (!categoryEl) {
        categoryEl = document.createElement('div');
        categoryEl.className = 'greeble-card-palette__category';
        categoryEl.dataset.category = category;

        const titleEl = document.createElement('h4');
        titleEl.className = 'greeble-card-palette__category-title';
        titleEl.textContent = this.options.categoryLabels[category] || category;
        categoryEl.appendChild(titleEl);

        const cardsEl = document.createElement('div');
        cardsEl.className = 'greeble-card-palette__cards';
        categoryEl.appendChild(cardsEl);

        this.container.appendChild(categoryEl);
      }

      const cardsContainer = categoryEl.querySelector('.greeble-card-palette__cards');
      
      grouped[category].forEach(cardData => {
        const card = GreebleDraggableCard.createCard(cardData, { container: cardsContainer });
        const instance = new GreebleDraggableCard(card, {
          onDragStart: this.options.onCardDragStart
        });
        this.cardInstances.push(instance);
      });
    });
  }

  // Highlight compatible cards based on output type
  highlightCompatible(outputType) {
    this.container.querySelectorAll('.greeble-draggable-card').forEach(card => {
      const accepts = card.dataset.accepts?.split(',') || [];
      const isCompatible = this.isTypeCompatible(outputType, accepts);
      
      card.classList.toggle('greeble-draggable-card--compatible', isCompatible);
      card.classList.toggle('greeble-draggable-card--incompatible', !isCompatible);
    });
  }

  clearHighlights() {
    this.container.querySelectorAll('.greeble-draggable-card').forEach(card => {
      card.classList.remove('greeble-draggable-card--compatible', 'greeble-draggable-card--incompatible');
    });
  }

  isTypeCompatible(outputType, acceptTypes) {
    if (acceptTypes.includes('any') || acceptTypes.includes('*')) return true;
    if (acceptTypes.includes(outputType)) return true;
    
    // JSON is compatible with text
    if (outputType === 'json' && acceptTypes.includes('text')) return true;
    if (outputType === 'text' && acceptTypes.includes('json')) return true;
    
    return false;
  }

  // Add cards dynamically
  addCard(cardData) {
    const category = cardData.category || 'default';
    let categoryEl = this.container.querySelector(`[data-category="${category}"]`);
    
    if (!categoryEl) {
      categoryEl = document.createElement('div');
      categoryEl.className = 'greeble-card-palette__category';
      categoryEl.dataset.category = category;

      const titleEl = document.createElement('h4');
      titleEl.className = 'greeble-card-palette__category-title';
      titleEl.textContent = this.options.categoryLabels[category] || category;
      categoryEl.appendChild(titleEl);

      const cardsEl = document.createElement('div');
      cardsEl.className = 'greeble-card-palette__cards';
      categoryEl.appendChild(cardsEl);

      this.container.appendChild(categoryEl);
    }

    const cardsContainer = categoryEl.querySelector('.greeble-card-palette__cards');
    const card = GreebleDraggableCard.createCard(cardData, { container: cardsContainer });
    
    const instance = new GreebleDraggableCard(card, {
      onDragStart: this.options.onCardDragStart
    });
    this.cardInstances.push(instance);

    return card;
  }

  // Filter cards by search term
  filter(searchTerm) {
    const term = searchTerm.toLowerCase();
    
    this.container.querySelectorAll('.greeble-draggable-card').forEach(card => {
      const title = card.querySelector('.greeble-draggable-card__title')?.textContent.toLowerCase() || '';
      const description = card.querySelector('.greeble-draggable-card__description')?.textContent.toLowerCase() || '';
      const matches = title.includes(term) || description.includes(term);
      card.style.display = matches ? '' : 'none';
    });

    // Hide empty categories
    this.container.querySelectorAll('.greeble-card-palette__category').forEach(category => {
      const visibleCards = category.querySelectorAll('.greeble-draggable-card:not([style*="display: none"])');
      category.style.display = visibleCards.length > 0 ? '' : 'none';
    });
  }

  clearFilter() {
    this.container.querySelectorAll('.greeble-draggable-card').forEach(card => {
      card.style.display = '';
    });
    this.container.querySelectorAll('.greeble-card-palette__category').forEach(category => {
      category.style.display = '';
    });
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-draggable]').forEach(el => {
    new GreebleDraggableCard(el);
  });

  document.querySelectorAll('[data-greeble-card-palette]').forEach(el => {
    new GreebleCardPalette(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { GreebleDraggableCard, GreebleCardPalette };
}
