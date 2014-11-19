'use strict';

module.exports = function (grunt) {
  var config = require('./gruntconfig');

  config.tasks.forEach(grunt.loadNpmTasks);
  grunt.initConfig(config);

  grunt.registerTask('lint', [
    'flake8'
  ]);

  grunt.registerTask('test', [
    'nose:main'
  ]);

  grunt.registerTask('default', [
    'lint',
    'jshint',
    'test',
    'watch'
  ]);
};
