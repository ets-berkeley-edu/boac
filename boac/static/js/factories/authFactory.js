(function(angular) {

  'use strict';

  angular.module('boac').factory('authFactory', function($http) {
    var devAuthLogIn = function(uid, password) {
      return $http.post('/devauth/login', {
        uid: uid,
        password: password
      });
    };

    var status = function() {
      return $http.get('/api/status');
    };

    return {
      devAuthLogIn: devAuthLogIn,
      status: status
    };
  });

}(window.angular));
