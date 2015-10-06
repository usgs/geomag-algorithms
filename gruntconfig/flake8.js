'use strict';

module.exports = {
  src: {
    options: {
      ignore: ['E122', 'E126', 'E127', 'E128', 'E131']
    },
    src: [
      'bin/*.py',
      'geomagio/**/*.py'
    ]
  },

  test: {
    options: {
      ignore: ['E122', 'E126', 'E127', 'E128', 'E131']
    },
    src: [
      'test/**/*.py'
    ]
  }
};
