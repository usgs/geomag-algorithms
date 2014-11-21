'use strict';

var config = require('./config');

module.exports = {
  main: {
    options: {
      match: '[Tt]est',
      verbose: true
    },
    src: [config.src + '/python']
  }
};
