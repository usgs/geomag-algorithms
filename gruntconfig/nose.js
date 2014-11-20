'use strict';

var config = require('./config');

module.exports = {
  main: {
    options: {
      match: '[Tt]est',
    },
    src: [config.src + '/python']
  }
};
