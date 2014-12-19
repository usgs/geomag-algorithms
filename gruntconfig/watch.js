'use strict';

module.exports = {
  scripts: {
    files: ['geomagio/**/*.py'],
    tasks: ['lint', 'test']
  },
  gruntfile: {
    files: ['Gruntfile.js', 'gruntconfig/**/*.js'],
    tasks: ['jshint:gruntfile']
  }
};
