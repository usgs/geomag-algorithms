'use strict';

module.exports = {
  scripts: {
    files: ['geomagio/**/*.py', 'bin/**/*.py'],
    tasks: ['lint', 'test']
  },
  gruntfile: {
    files: ['Gruntfile.js', 'gruntconfig/**/*.js'],
    tasks: ['jshint:gruntfile']
  }
};
