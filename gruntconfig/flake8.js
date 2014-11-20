'use strict';

var config = require('./config');

module.exports = {
  options: {
    ignore: ['E122', 'E126', 'E127', 'E128', 'E131']
  },
  src: [ config.src + '/**/*.py' ]
};
