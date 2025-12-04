/**
 * Greeble Drop Zone
 * Generic drag-and-drop file upload component.
 * 
 * Usage:
 *   const dropZone = new GreebleDropZone('#drop-zone', {
 *     accept: ['.pdf', '.docx', '.txt'],
 *     maxSize: 10 * 1024 * 1024, // 10MB
 *     multiple: true,
 *     onFilesSelected: (files) => { ... }
 *   });
 */
class GreebleDropZone {
  constructor(selector, options = {}) {
    this.container = typeof selector === 'string' 
      ? document.querySelector(selector) 
      : selector;
    
    if (!this.container) {
      console.error('GreebleDropZone: Container not found');
      return;
    }

    // Read options from data attributes or passed options
    this.options = {
      accept: this.parseAccept(this.container.dataset.accept) || ['*'],
      maxSize: parseInt(this.container.dataset.maxSize) || 10 * 1024 * 1024,
      multiple: this.container.dataset.multiple !== 'false',
      onFilesSelected: null,
      onFileRemoved: null,
      onUploadStart: null,
      onUploadProgress: null,
      onUploadComplete: null,
      onError: null,
      ...options
    };

    this.files = [];
    this.init();
  }

  parseAccept(acceptStr) {
    if (!acceptStr) return null;
    return acceptStr.split(',').map(s => s.trim());
  }

  init() {
    this.input = this.container.querySelector('#drop-zone-input');
    this.filesContainer = this.container.querySelector('#drop-zone-files');
    this.actionsContainer = this.container.querySelector('#drop-zone-actions');
    this.clearBtn = this.container.querySelector('#drop-zone-clear');
    this.uploadBtn = this.container.querySelector('#drop-zone-upload');

    // Set input attributes
    if (this.input) {
      if (this.options.accept && this.options.accept[0] !== '*') {
        this.input.accept = this.options.accept.join(',');
      }
      this.input.multiple = this.options.multiple;
    }

    this.bindEvents();
  }

  bindEvents() {
    // Click to open file dialog
    this.container.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      this.input?.click();
    });

    // File input change
    if (this.input) {
      this.input.addEventListener('change', (e) => {
        this.handleFiles(e.target.files);
      });
    }

    // Drag events
    this.container.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.container.classList.add('greeble-drop-zone--dragover');
    });

    this.container.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.container.classList.remove('greeble-drop-zone--dragover');
    });

    this.container.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.container.classList.remove('greeble-drop-zone--dragover');
      this.handleFiles(e.dataTransfer.files);
    });

    // Clear button
    if (this.clearBtn) {
      this.clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.clear();
      });
    }

    // Upload button - prepare FormData for HTMX
    if (this.uploadBtn) {
      this.uploadBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.prepareUpload();
      });

      // HTMX integration
      this.uploadBtn.addEventListener('htmx:configRequest', (e) => {
        this.files.forEach((file, index) => {
          e.detail.parameters[`file_${index}`] = file;
        });
      });
    }
  }

  handleFiles(fileList) {
    const newFiles = Array.from(fileList);
    const validFiles = [];
    const errors = [];

    newFiles.forEach(file => {
      // Check file type
      if (!this.isValidType(file)) {
        errors.push(`${file.name}: Invalid file type`);
        return;
      }

      // Check file size
      if (file.size > this.options.maxSize) {
        errors.push(`${file.name}: File too large (max ${this.formatSize(this.options.maxSize)})`);
        return;
      }

      validFiles.push(file);
    });

    if (errors.length > 0) {
      this.handleError(errors);
    }

    if (validFiles.length > 0) {
      if (this.options.multiple) {
        this.files = [...this.files, ...validFiles];
      } else {
        this.files = [validFiles[0]];
      }
      this.renderFiles();
      this.updateUI();

      if (this.options.onFilesSelected) {
        this.options.onFilesSelected(this.files);
      }

      this.container.dispatchEvent(new CustomEvent('greeble:dropzone:files', {
        bubbles: true,
        detail: { files: this.files }
      }));
    }
  }

  isValidType(file) {
    if (this.options.accept[0] === '*') return true;

    const fileName = file.name.toLowerCase();
    const mimeType = file.type.toLowerCase();

    return this.options.accept.some(accept => {
      accept = accept.toLowerCase();
      
      // Extension match
      if (accept.startsWith('.')) {
        return fileName.endsWith(accept);
      }
      
      // MIME type match
      if (accept.includes('/')) {
        if (accept.endsWith('/*')) {
          return mimeType.startsWith(accept.replace('/*', '/'));
        }
        return mimeType === accept;
      }

      return false;
    });
  }

  renderFiles() {
    if (!this.filesContainer) return;

    // Clear existing content
    this.filesContainer.innerHTML = '';

    this.files.forEach((file, index) => {
      const fileEl = document.createElement('div');
      fileEl.className = 'greeble-drop-zone__file';
      fileEl.dataset.index = index;

      // File icon (static SVG, safe to use innerHTML)
      const iconWrapper = document.createElement('div');
      iconWrapper.className = 'greeble-drop-zone__file-icon-wrapper';
      iconWrapper.innerHTML = `<svg class="greeble-drop-zone__file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
      </svg>`;
      fileEl.appendChild(iconWrapper.firstElementChild);

      // File info
      const info = document.createElement('div');
      info.className = 'greeble-drop-zone__file-info';

      const nameEl = document.createElement('p');
      nameEl.className = 'greeble-drop-zone__file-name';
      nameEl.textContent = file.name;
      info.appendChild(nameEl);

      const sizeEl = document.createElement('p');
      sizeEl.className = 'greeble-drop-zone__file-size';
      sizeEl.textContent = this.formatSize(file.size);
      info.appendChild(sizeEl);

      fileEl.appendChild(info);

      // Remove button
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'greeble-drop-zone__file-remove';
      removeBtn.dataset.index = index;
      removeBtn.setAttribute('aria-label', `Remove ${file.name}`);
      removeBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>`;
      removeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeFile(index);
      });
      fileEl.appendChild(removeBtn);

      this.filesContainer.appendChild(fileEl);
    });
  }

  removeFile(index) {
    const removed = this.files.splice(index, 1)[0];
    this.renderFiles();
    this.updateUI();

    if (this.options.onFileRemoved) {
      this.options.onFileRemoved(removed, this.files);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:dropzone:remove', {
      bubbles: true,
      detail: { removed, files: this.files }
    }));
  }

  updateUI() {
    const hasFiles = this.files.length > 0;
    
    this.container.classList.toggle('greeble-drop-zone--has-files', hasFiles);
    
    if (this.filesContainer) {
      this.filesContainer.hidden = !hasFiles;
    }
    
    if (this.actionsContainer) {
      this.actionsContainer.hidden = !hasFiles;
    }
  }

  clear() {
    this.files = [];
    if (this.input) {
      this.input.value = '';
    }
    this.renderFiles();
    this.updateUI();
    this.container.classList.remove('greeble-drop-zone--error');

    this.container.dispatchEvent(new CustomEvent('greeble:dropzone:clear', {
      bubbles: true
    }));
  }

  prepareUpload() {
    if (this.files.length === 0) return;

    const formData = new FormData();
    this.files.forEach((file, index) => {
      formData.append(`file_${index}`, file);
    });

    if (this.options.onUploadStart) {
      this.options.onUploadStart(this.files, formData);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:dropzone:upload', {
      bubbles: true,
      detail: { files: this.files, formData }
    }));
  }

  handleError(errors) {
    this.container.classList.add('greeble-drop-zone--error');
    
    if (this.options.onError) {
      this.options.onError(errors);
    }

    this.container.dispatchEvent(new CustomEvent('greeble:dropzone:error', {
      bubbles: true,
      detail: { errors }
    }));

    // Auto-remove error state
    setTimeout(() => {
      this.container.classList.remove('greeble-drop-zone--error');
    }, 3000);
  }

  formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Public API
  getFiles() {
    return this.files;
  }

  addFiles(files) {
    this.handleFiles(files);
  }

  setAccept(accept) {
    this.options.accept = Array.isArray(accept) ? accept : [accept];
    if (this.input) {
      this.input.accept = this.options.accept.join(',');
    }
  }
}

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-greeble-drop-zone]').forEach(el => {
    new GreebleDropZone(el);
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GreebleDropZone;
}
