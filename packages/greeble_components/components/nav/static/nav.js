/**
 * Greeble Nav Component
 * Handles mobile toggle, scroll spy, and active state management
 */

(function () {
  'use strict';

  function initNav(nav) {
    const toggle = nav.querySelector('.greeble-nav__toggle');
    const links = nav.querySelectorAll('.greeble-nav__link[href^="#"]');

    // Mobile toggle
    if (toggle) {
      toggle.addEventListener('click', () => {
        const isOpen = nav.dataset.open === 'true';
        nav.dataset.open = String(!isOpen);
        toggle.setAttribute('aria-expanded', String(!isOpen));
      });
    }

    // Close menu when clicking a link (mobile)
    links.forEach(link => {
      link.addEventListener('click', () => {
        nav.dataset.open = 'false';
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
      });
    });

    // Scroll spy: highlight active section
    if (links.length > 0) {
      const sections = Array.from(links)
        .map(link => {
          const id = link.getAttribute('href')?.slice(1);
          return id ? document.getElementById(id) : null;
        })
        .filter(Boolean);

      if (sections.length > 0) {
        const observer = new IntersectionObserver(
          (entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                const id = entry.target.id;
                links.forEach(link => {
                  const isActive = link.getAttribute('href') === `#${id}`;
                  link.dataset.active = String(isActive);
                });
              }
            });
          },
          {
            rootMargin: '-20% 0px -70% 0px',
            threshold: 0,
          }
        );

        sections.forEach(section => observer.observe(section));
      }
    }

    // Close menu on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && nav.dataset.open === 'true') {
        nav.dataset.open = 'false';
        if (toggle) {
          toggle.setAttribute('aria-expanded', 'false');
          toggle.focus();
        }
      }
    });

    // Close menu on click outside
    document.addEventListener('click', (e) => {
      if (nav.dataset.open === 'true' && !nav.contains(e.target)) {
        nav.dataset.open = 'false';
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Initialize all nav components
  function init() {
    document.querySelectorAll('[data-greeble-nav]').forEach(initNav);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-init after HTMX swaps
  document.addEventListener('htmx:afterSwap', (e) => {
    const nav = e.detail.target.querySelector?.('[data-greeble-nav]');
    if (nav) initNav(nav);
  });
})();
