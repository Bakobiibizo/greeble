/**
 * Greeble Mobile Menu Component
 * Handles focus trap, keyboard navigation, and close behaviors
 */

(function () {
  'use strict';

  function initMobileMenu(menu) {
    const panel = menu.querySelector('.greeble-mobile-menu__panel');
    const closeBtn = menu.querySelector('.greeble-mobile-menu__close');
    const backdrop = menu.querySelector('.greeble-mobile-menu__backdrop');

    // Get all focusable elements
    const focusableSelector = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    const focusableElements = panel?.querySelectorAll(focusableSelector);
    const firstFocusable = focusableElements?.[0];
    const lastFocusable = focusableElements?.[focusableElements.length - 1];

    // Focus first element on open
    if (firstFocusable) {
      firstFocusable.focus();
    }

    // Prevent body scroll
    document.body.style.overflow = 'hidden';

    // Focus trap
    function handleKeydown(e) {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          // Shift + Tab
          if (document.activeElement === firstFocusable) {
            e.preventDefault();
            lastFocusable?.focus();
          }
        } else {
          // Tab
          if (document.activeElement === lastFocusable) {
            e.preventDefault();
            firstFocusable?.focus();
          }
        }
      }

      // Close on Escape
      if (e.key === 'Escape') {
        closeMenu();
      }
    }

    function closeMenu() {
      // Restore body scroll
      document.body.style.overflow = '';
      
      // Trigger HTMX close if available
      if (closeBtn && window.htmx) {
        htmx.trigger(closeBtn, 'click');
      } else {
        // Fallback: remove menu
        menu.remove();
      }
    }

    // Event listeners
    document.addEventListener('keydown', handleKeydown);

    // Cleanup when menu is removed
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.removedNodes.forEach((node) => {
          if (node === menu || node.contains?.(menu)) {
            document.removeEventListener('keydown', handleKeydown);
            document.body.style.overflow = '';
            observer.disconnect();
          }
        });
      });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Store cleanup function
    menu._greebleCleanup = () => {
      document.removeEventListener('keydown', handleKeydown);
      document.body.style.overflow = '';
      observer.disconnect();
    };
  }

  // Initialize all mobile menu components
  function init() {
    document.querySelectorAll('[data-greeble-mobile-menu]').forEach(initMobileMenu);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-init after HTMX swaps
  document.addEventListener('htmx:afterSwap', (e) => {
    const menu = e.detail.target.querySelector?.('[data-greeble-mobile-menu]');
    if (menu) initMobileMenu(menu);
  });

  // Cleanup before HTMX removes menu
  document.addEventListener('htmx:beforeSwap', (e) => {
    const menu = e.detail.target.querySelector?.('[data-greeble-mobile-menu]');
    if (menu?._greebleCleanup) {
      menu._greebleCleanup();
    }
  });
})();
