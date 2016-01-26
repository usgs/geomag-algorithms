'use strict';

module.exports = {
  clean: require('./clean'),
  flake8: require('./flake8'),
  jshint: require('./jshint'),
  nose: require('./nose'),
  watch: require('./watch'),
  // task node module names
  tasks: [
    'grunt-contrib-clean',
    'grunt-contrib-jshint',
    'grunt-contrib-watch',
    'grunt-flake8',
    'grunt-nose'
  ]
};
