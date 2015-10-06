'use strict';

module.exports = {
  gruntfile: {
    files: [
      'Gruntfile.js',
      'gruntconfig/**/*.js'
    ],
    tasks: [
      'jshint:gruntfile'
    ]
  },
  scripts: {
    files: [
      'bin/**/*.py',
      'geomagio/**/*.py'
    ],
    tasks: [
      'flake8:src',
      'test'
    ]
  },
  tests: {
    files: [
      'test/**/*.py'
    ],
    tasks: [
      'flake8:test',
      'test'
    ]
  }
};
