module.exports = {
  theme: {
    extend: {
      colors: {
        background: 'var(--greeble-color-background, #ffffff)',
        foreground: 'var(--greeble-color-foreground, #111111)',
        muted: 'var(--greeble-color-muted, #808080)',
        accent: 'var(--greeble-color-accent, #0078d4)'
      },
      borderRadius: {
        none: 'var(--greeble-radius-none, 0px)',
        sm: 'var(--greeble-radius-small, 6px)',
        DEFAULT: 'var(--greeble-radius-default, 10px)',
        md: 'var(--greeble-radius-medium, 12px)',
        lg: 'var(--greeble-radius-large, 16px)',
        xl: 'var(--greeble-radius-xlarge, 20px)',
        '2xl': 'var(--greeble-radius-2xlarge, 24px)',
        '3xl': 'var(--greeble-radius-3xlarge, 32px)',
        full: 'var(--greeble-radius-full, 9999px)'
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
