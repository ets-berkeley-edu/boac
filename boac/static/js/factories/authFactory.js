(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('authFactory', function(me, $http, $rootScope) {

    var refreshStatus = function() {
      return $http.get('/api/status').then(function(results) {
        var data = results.data;
        // Refresh module value in case other controllers, factories, etc. do a lookup in the current page context.
        boac.value('me', data);
        // Refresh instance currently referenced in templates
        $rootScope.me = data;
        return;
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
      return $http.post('/devauth/login', credentials).then(refreshStatus);
    };

    var logOut = function() {
      return $http.get('/logout').then(function(results) {
        window.location = results.data.cas_logout_url;
      });
    };

    // Make current user available to templates
    $rootScope.me = me;

    return {
      casLogIn: casLogIn,
      devAuthLogIn: devAuthLogIn,
      logOut: logOut
    };
  });

}(window.angular));
