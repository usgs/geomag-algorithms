'use strict';

var config = require('./config');

module.exports = {
  options: {
    ignore: ['E126']
  },
  src: [ config.src + '/**/*.py' ]
};
