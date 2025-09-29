const theme = require('./theme.cjs');

const { extend, createPreset } = theme;

function withContent(content, options = {}) {
  const list = Array.isArray(content) ? content : [content];
  return createPreset({ ...options, content: list });
}

const preset = createPreset();

Object.defineProperties(preset, {
  default: { value: preset },
  preset: { value: preset },
  extend: { value: extend },
  createPreset: { value: createPreset },
  withContent: { value: withContent },
});

module.exports = preset;
