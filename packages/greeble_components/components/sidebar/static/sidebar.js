/**
 * Greeble Sidebar Component
 * Handles collapsible groups, scroll spy, and active state management
 */

(function () {
  'use strict';

  function initSidebar(sidebar) {
    const toggles = sidebar.querySelectorAll('.greeble-sidebar__group-toggle');
    const links = sidebar.querySelectorAll('.greeble-sidebar__link[href^="#"]');

    // Group toggle functionality
    toggles.forEach(toggle => {
      toggle.addEventListener('click', () => {
        const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!isExpanded));
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
                  
                  // Expand parent group if active
                  if (isActive) {
                    const group = link.closest('.greeble-sidebar__group');
                    const groupToggle = group?.querySelector('.greeble-sidebar__group-toggle');
                    if (groupToggle) {
                      groupToggle.setAttribute('aria-expanded', 'true');
                    }
                  }
                });
              }
            });
          },
          {
            rootMargin: '-10% 0px -80% 0px',
            threshold: 0,
          }
        );

        sections.forEach(section => observer.observe(section));
      }
    }

    // Smooth scroll on link click
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href?.startsWith('#')) {
          const target = document.getElementById(href.slice(1));
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Update active state immediately
            links.forEach(l => l.dataset.active = 'false');
            link.dataset.active = 'true';
            
            // Update URL hash without jumping
            history.pushState(null, '', href);
          }
        }
      });
    });

    // Collapse all groups except first (optional)
    // Uncomment to start with collapsed groups:
    // toggles.forEach((toggle, i) => {
    //   if (i > 0) toggle.setAttribute('aria-expanded', 'false');
    // });
  }

  // Initialize all sidebar components
  function init() {
    document.querySelectorAll('[data-greeble-sidebar]').forEach(initSidebar);
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Re-init after HTMX swaps
  document.addEventListener('htmx:afterSwap', (e) => {
    const sidebar = e.detail.target.querySelector?.('[data-greeble-sidebar]');
    if (sidebar) initSidebar(sidebar);
  });
})();
