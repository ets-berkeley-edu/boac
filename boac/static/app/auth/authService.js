(function(angular) {

  'use strict';

  angular.module('boac').service('authService', function(authFactory, googleAnalyticsService, $http, $location, $rootScope) {

    var isAuthenticatedUser = function() {
      return $rootScope.me && $rootScope.me.authenticated_as.is_authenticated;
    };

    var reloadMe = function() {
      return $http.get('/api/status').then(authFactory.loadUserProfile).then(function() {
        var me = $rootScope.me.authenticated_as;
        if (me.is_authenticated && $location.search().casLogin) {
          // Track CAS login event
          googleAnalyticsService.track('user', 'login', me.uid, parseInt(me.uid, 10));
        }
        return me;
      });
    };

    return {
      isAuthenticatedUser: isAuthenticatedUser,
      reloadMe: reloadMe
    };
  });

}(window.angular));
