'use strict';

module.exports = function (grunt) {
  var config = require('./gruntconfig');

  config.tasks.forEach(grunt.loadNpmTasks);
  grunt.initConfig(config);

  grunt.registerTask('test', [
    'nose:main'
  ]);

  grunt.registerTask('default', [
    'flake8',
    'jshint',
    'test',
    'watch'
  ]);
};
