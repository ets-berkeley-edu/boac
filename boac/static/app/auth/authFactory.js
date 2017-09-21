(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('authFactory', function($http, $rootScope) {

    var refreshStatus = function() {
      return $http.get('/api/status').then(function(results) {
        // Refresh instance currently referenced in templates
        $rootScope.me = results.data;
      });
    };

    var casLogIn = function() {
      return $http.get('/cas/login_url').then(function(results) {
        window.location = results.data.cas_login_url;
      });
    };

    var devAuthLogIn = function(uid, password) {
      var credentials = {
        uid: uid,
        password: password
      };
      return $http.post('/devauth/login', credentials).then(
        function successCallback() {
          $rootScope.$emit('authenticationSuccess');
          refreshStatus();
        },
        function errorCallback() {
          $rootScope.$emit('authenticationFailure');
          $rootScope.me = null;
        });
    };

    var logOut = function() {
      return $http.get('/logout').then(function(results) {
        window.location = results.data.cas_logout_url;
      });
    };

    return {
      casLogIn: casLogIn,
      devAuthLogIn: devAuthLogIn,
      logOut: logOut
    };
  });

}(window.angular));
