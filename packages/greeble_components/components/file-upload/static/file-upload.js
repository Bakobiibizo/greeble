/**
 * Greeble File Upload
 * Multi-mode file upload with tabs for file, URL, and paste input.
 * 
 * Usage:
 *   const upload = new GreebleFileUpload('#file-upload', {
 *     accept: ['image/*', '.pdf', '.docx'],
 *     maxSize: 10 * 1024 * 1024,
 *     onInput: (data, type, mode) => { ... }
 *   });
 */
class GreebleFileUpload {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;
    
    if (!this.container) {
      console.error('GreebleFileUpload: Container not found');
      return;
    }

    this.options = {
      accept: ['*/*'],
      maxSize: 50 * 1024 * 1024, // 50MB default
      fetchEndpoint: '/api/fetch-url',
      onInput: null,
      onTabChange: null,
      onError: null,
      ...options
    };

    this.currentTab = 'file';
    this.currentFile = null;
    this.currentUrl = null;
    this.currentPaste = null;

    this.init();
  }

  init() {
    // Tab elements
    this.tabs = this.container.querySelectorAll('.greeble-file-upload__tab');
    this.panels = this.container.querySelectorAll('.greeble-file-upload__panel');

    // File elements
    this.droparea = this.container.querySelector('#file-upload-droparea');
    this.fileInput = this.container.querySelector('#file-upload-input');
    this.fileInfo = this.container.querySelector('#file-upload-file-info');
    this.filePreview = this.container.querySelector('#file-upload-preview');
    this.fileName = this.container.querySelector('#file-upload-filename');
    this.fileSize = this.container.querySelector('#file-upload-filesize');
    this.removeBtn = this.container.querySelector('#file-upload-remove');

    // URL elements
    this.urlInput = this.container.querySelector('#file-upload-url');
    this.fetchBtn = this.container.querySelector('#file-upload-fetch');

    // Paste elements
    this.pasteArea = this.container.querySelector('#file-upload-paste');

    // Type badge
    this.typeBadge = this.container.querySelector('#file-upload-type-badge');
    this.typeContainer = this.container.querySelector('#file-upload-type');

    this.bindEvents();
  }

  bindEvents() {
    // Tab switching
    this.tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        this.switchTab(tab.dataset.tab);
      });
    });

    // File input
    if (this.fileInput) {
      this.fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) {
          this.handleFile(e.target.files[0]);
        }
      });
    }

    // Drag and drop
    if (this.droparea) {
      this.droparea.addEventListener('dragover', (e) => {
        e.preventDefault();
        this.droparea.classList.add('greeble-file-upload__droparea--dragover');
      });

      this.droparea.addEventListener('dragleave', () => {
        this.droparea.classList.remove('greeble-file-upload__droparea--dragover');
      });

      this.droparea.addEventListener('drop', (e) => {
        e.preventDefault();
        this.droparea.classList.remove('greeble-file-upload__droparea--dragover');
        if (e.dataTransfer.files[0]) {
          this.handleFile(e.dataTransfer.files[0]);
        }
      });
    }

    // Remove file
    if (this.removeBtn) {
      this.removeBtn.addEventListener('click', () => this.clearFile());
    }

    // URL fetch
    if (this.fetchBtn) {
      this.fetchBtn.addEventListener('click', () => this.fetchUrl());
    }

    if (this.urlInput) {
      this.urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.fetchUrl();
        }
      });

      this.urlInput.addEventListener('input', () => {
        this.currentUrl = this.urlInput.value;
        this.emitInput();
      });
    }

    // Paste area
    if (this.pasteArea) {
      this.pasteArea.addEventListener('input', () => {
        this.currentPaste = this.pasteArea.value;
        this.detectPasteType();
        this.emitInput();
      });
    }

    // Global paste handler
    this.container.addEventListener('paste', (e) => {
      if (this.currentTab === 'file' && e.clipboardData.files.length > 0) {
        e.preventDefault();
        this.handleFile(e.clipboardData.files[0]);
      }
    });
  }

  switchTab(tabName) {
    this.currentTab = tabName;

    // Update tab states
    this.tabs.forEach(tab => {
      const isActive = tab.dataset.tab === tabName;
      tab.classList.toggle('greeble-file-upload__tab--active', isActive);
      tab.setAttribute('aria-selected', isActive);
    });

    // Update panel states
    this.panels.forEach(panel => {
      const isActive = panel.dataset.panel === tabName;
      panel.classList.toggle('greeble-file-upload__panel--active', isActive);
      panel.hidden = !isActive;
    });

    if (this.options.onTabChange) {
      this.options.onTabChange(tabName);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:fileupload:tab', {
      bubbles: true,
      detail: { tab: tabName }
    }));
  }

  handleFile(file) {
    // Validate size
    if (file.size > this.options.maxSize) {
      this.handleError(`File too large. Maximum size is ${this.formatSize(this.options.maxSize)}`);
      return;
    }

    // Validate type
    if (!this.isValidType(file)) {
      this.handleError('Invalid file type');
      return;
    }

    this.currentFile = file;

    // Update UI
    if (this.droparea) this.droparea.hidden = true;
    if (this.fileInfo) this.fileInfo.hidden = false;
    if (this.fileName) this.fileName.textContent = file.name;
    if (this.fileSize) this.fileSize.textContent = this.formatSize(file.size);

    // Show preview
    this.showFilePreview(file);

    // Update type badge
    this.updateTypeBadge(this.getFileType(file));

    this.emitInput();
  }

  showFilePreview(file) {
    if (!this.filePreview) return;

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.filePreview.innerHTML = `<img src="${e.target.result}" alt="${file.name}">`;
      };
      reader.readAsDataURL(file);
    } else {
      // Show icon based on type
      const icon = this.getFileIcon(file);
      this.filePreview.innerHTML = icon;
    }
  }

  getFileIcon(file) {
    const type = file.type || '';
    
    if (type.startsWith('audio/')) {
      return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>`;
    }
    if (type.startsWith('video/')) {
      return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/></svg>`;
    }
    if (type === 'application/pdf') {
      return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>`;
    }
    
    // Default document icon
    return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
  }

  getFileType(file) {
    const type = file.type || '';
    const ext = file.name.split('.').pop().toLowerCase();

    if (type.startsWith('image/')) return 'image';
    if (type.startsWith('audio/')) return 'audio';
    if (type.startsWith('video/')) return 'video';
    if (type === 'application/json' || ext === 'json') return 'json';
    if (type === 'text/markdown' || ext === 'md') return 'markdown';
    if (['pdf', 'docx', 'doc', 'txt', 'html', 'xml'].includes(ext)) return 'docs';
    
    return 'text';
  }

  clearFile() {
    this.currentFile = null;
    if (this.fileInput) this.fileInput.value = '';
    if (this.droparea) this.droparea.hidden = false;
    if (this.fileInfo) this.fileInfo.hidden = true;
    if (this.filePreview) this.filePreview.innerHTML = '';
    this.updateTypeBadge(null);
    this.emitInput();
  }

  async fetchUrl() {
    const url = this.urlInput?.value;
    if (!url) return;

    try {
      this.fetchBtn.disabled = true;
      this.fetchBtn.textContent = 'Fetching...';

      // Emit URL input event - actual fetching handled by server
      this.currentUrl = url;
      this.updateTypeBadge('docs');
      this.emitInput();

      this.container.dispatchEvent(new CustomEvent('greeble:fileupload:fetch', {
        bubbles: true,
        detail: { url }
      }));

    } catch (error) {
      this.handleError('Failed to fetch URL');
    } finally {
      this.fetchBtn.disabled = false;
      this.fetchBtn.textContent = 'Fetch';
    }
  }

  detectPasteType() {
    const content = this.currentPaste || '';
    let type = 'text';

    // Try to detect JSON
    try {
      JSON.parse(content);
      type = 'json';
    } catch {
      // Check for markdown indicators
      if (/^#|^\*\*|^\-\s|^\d+\.\s|```/.test(content)) {
        type = 'markdown';
      }
      // Check for HTML
      else if (/<[a-z][\s\S]*>/i.test(content)) {
        type = 'docs';
      }
    }

    this.updateTypeBadge(type);
  }

  updateTypeBadge(type) {
    if (!this.typeBadge || !this.typeContainer) return;

    if (!type) {
      this.typeContainer.hidden = true;
      return;
    }

    this.typeContainer.hidden = false;
    this.typeBadge.textContent = type;
    this.typeBadge.className = `greeble-type-badge greeble-type-badge--${type}`;
  }

  isValidType(file) {
    if (this.options.accept.includes('*/*')) return true;

    const fileName = file.name.toLowerCase();
    const mimeType = file.type.toLowerCase();

    return this.options.accept.some(accept => {
      accept = accept.toLowerCase();
      if (accept.startsWith('.')) {
        return fileName.endsWith(accept);
      }
      if (accept.endsWith('/*')) {
        return mimeType.startsWith(accept.replace('/*', '/'));
      }
      return mimeType === accept;
    });
  }

  handleError(message) {
    if (this.options.onError) {
      this.options.onError(message);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:fileupload:error', {
      bubbles: true,
      detail: { message }
    }));
  }

  emitInput() {
    const data = this.getData();
    
    if (this.options.onInput) {
      this.options.onInput(data.value, data.type, data.mode);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:fileupload:input', {
      bubbles: true,
      detail: data
    }));
  }

  formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  // Public API
  getData() {
    switch (this.currentTab) {
      case 'file':
        return {
          mode: 'file',
          value: this.currentFile,
          type: this.currentFile ? this.getFileType(this.currentFile) : null
        };
      case 'url':
        return {
          mode: 'url',
          value: this.currentUrl,
          type: 'docs'
        };
      case 'paste':
        return {
          mode: 'paste',
          value: this.currentPaste,
          type: this.currentPaste ? 'text' : null
        };
      default:
        return { mode: null, value: null, type: null };
    }
  }

  clear() {
    this.clearFile();
    if (this.urlInput) this.urlInput.value = '';
    if (this.pasteArea) this.pasteArea.value = '';
    this.currentUrl = null;
    this.currentPaste = null;
    this.updateTypeBadge(null);
  }

  setAccept(accept) {
    this.options.accept = Array.isArray(accept) ? accept : [accept];
    if (this.fileInput) {
      this.fileInput.accept = this.options.accept.join(',');
    }
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-file-upload]').forEach(el => {
    new GreebleFileUpload(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleFileUpload;
}
