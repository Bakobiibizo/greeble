const colors = {
  background: 'var(--greeble-color-background, #0b0b0c)',
  surface: 'var(--greeble-color-background, #0b0b0c)',
  foreground: 'var(--greeble-color-foreground, #e8e8ea)',
  muted: 'var(--greeble-color-muted, #a0a0a7)',
  accent: 'var(--greeble-color-accent, #6aa1ff)',
  'accent-foreground': 'var(--greeble-color-background, #0b0b0c)',
};

const borderRadiusBase = 'var(--greeble-radius-medium, 12px)';
const borderRadius = {
  none: '0px',
  sm: `calc(${borderRadiusBase} / 2)`,
  DEFAULT: borderRadiusBase,
  md: `calc(${borderRadiusBase} * 1.25)`,
  lg: `calc(${borderRadiusBase} * 1.5)`,
  full: '9999px',
};

const spacingBase = {
  1: 'var(--greeble-spacing-1, 0.25rem)',
  2: 'var(--greeble-spacing-2, 0.5rem)',
  3: 'var(--greeble-spacing-3, 0.75rem)',
  4: 'var(--greeble-spacing-4, 1rem)',
};

const spacing = {
  ...spacingBase,
  xs: spacingBase[1],
  sm: spacingBase[2],
  md: spacingBase[3],
  lg: spacingBase[4],
};

const boxShadow = {
  DEFAULT: 'var(--greeble-shadow-1, 0 1px 2px rgba(0, 0, 0, 0.2))',
  sm: 'var(--greeble-shadow-1, 0 1px 2px rgba(0, 0, 0, 0.2))',
  md: 'var(--greeble-shadow-2, 0 8px 30px rgba(0, 0, 0, 0.35))',
  lg: 'var(--greeble-shadow-2, 0 8px 30px rgba(0, 0, 0, 0.35))',
  focus: 'var(--greeble-focus-ring, 0 0 0 3px rgba(106, 161, 255, 0.5))',
};

const fontFamily = {
  sans: 'var(--greeble-font-sans, "Inter", "Helvetica Neue", system-ui, -apple-system, sans-serif)',
  display: 'var(--greeble-font-display, "Satoshi", "Inter", system-ui, sans-serif)',
  mono: 'var(--greeble-font-mono, "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, monospace)',
};

const extend = {
  colors,
  borderColor: {
    DEFAULT: colors.muted,
  },
  borderRadius,
  boxShadow,
  fontFamily,
  ringColor: {
    DEFAULT: colors.accent,
  },
  ringOffsetColor: {
    DEFAULT: colors.background,
  },
  outlineColor: {
    DEFAULT: colors.accent,
  },
  spacing,
};

function createPreset(options = {}) {
  const {
    content = [],
    darkMode = 'class',
    plugins = [],
  } = options;

  return {
    content,
    darkMode,
    theme: {
      extend,
    },
    plugins,
  };
}

const preset = createPreset();

module.exports = {
  extend,
  createPreset,
  preset,
};
