'use strict';

const preset = require('./preset.cjs');

module.exports = preset;
module.exports.default = preset;
module.exports.createPreset = preset.createPreset;
module.exports.extend = preset.extend;
module.exports.withContent = preset.withContent;
