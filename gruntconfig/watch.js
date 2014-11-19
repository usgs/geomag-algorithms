'use strict';

var config = require('./config');

module.exports = {
  scripts: {
    files: [config.src + '/**/*.py'],
    tasks: ['lint', 'test']
  },
  gruntfile: {
    files: ['Gruntfile.js', 'gruntconfig/**/*.js'],
    tasks: ['jshint:gruntfile']
  }
};
