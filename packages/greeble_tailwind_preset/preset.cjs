// Greeble Tailwind Preset
// Maps Greeble CSS token variables to Tailwind theme scales.
// Usage: in your tailwind.config.cjs
//   module.exports = {
//     presets: [require('./tools/greeble/tailwind/preset.cjs')],
//     content: ['./templates/**/*.html']
//   }

/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'rgb(var(--greeble-color-background) / <alpha-value>)',
        foreground: 'rgb(var(--greeble-color-foreground) / <alpha-value>)',
        muted: 'rgb(var(--greeble-color-muted) / <alpha-value>)',
        accent: 'rgb(var(--greeble-color-accent) / <alpha-value>)'
      },
      borderRadius: {
        md: 'var(--greeble-radius-medium)'
      },
      boxShadow: {
        g1: 'var(--greeble-shadow-1)',
        g2: 'var(--greeble-shadow-2)'
      },
      spacing: {
        1: 'var(--greeble-spacing-1)',
        2: 'var(--greeble-spacing-2)',
        3: 'var(--greeble-spacing-3)',
        4: 'var(--greeble-spacing-4)'
      }
    }
  }
};
