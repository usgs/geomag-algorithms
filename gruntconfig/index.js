'use strict';

module.exports = {
  flake8: require('./flake8'),
  jshint: require('./jshint'),
  nose: require('./nose'),
  watch: require('./watch'),
  // task node module names
  tasks: [
    'grunt-contrib-jshint',
    'grunt-contrib-watch',
    'grunt-flake8',
    'grunt-nose'
  ]
};
