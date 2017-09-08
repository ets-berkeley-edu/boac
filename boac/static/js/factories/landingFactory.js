(function(angular) {

  'use strict';

  angular.module('boac').factory('landingFactory', function($http) {
    var getAppState = function() {
      return $http.get('/api/status');
    };

    return {
      'getAppState': getAppState
    };
  });

}(window.angular));
