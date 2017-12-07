(function(angular) {

  'use strict';

  angular.module('boac').service('utilService', function() {

    var format = function(str, tokens) {
      var formatted = str;
      _.each(tokens, function(value, key) {
        formatted = formatted.replace('${' + key + '}', value);
      });
      return formatted;
    };

    return {
      format: format
    };
  });

}(window.angular));
