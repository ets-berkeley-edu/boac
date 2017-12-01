(function(angular) {

  'use strict';

  angular.module('boac').service('authService', function(authFactory, googleAnalyticsService, $http, $location, $rootScope, $state) {

    var isAuthenticatedUser = function() {
      return $rootScope.me && $rootScope.me.authenticated_as.is_authenticated;
    };

    var init = function() {
      $http.get('/api/status').then(authFactory.loadUserProfile).then(function() {
        var me = $rootScope.me.authenticated_as;
        if (me.is_authenticated && $location.search().casLogin) {
          // Track CAS login event
          googleAnalyticsService.track('user', 'login', me.uid, parseInt(me.uid, 10));
        }
        if (!$state.current.isPublic && !me.is_authenticated) {
          $location.path('/');
          $location.replace();
        }
      });
    };

    var authWrap = function(controllerMain) {
      var decoratedFunction = function() {
        if (isAuthenticatedUser()) {
          controllerMain();
        }
      };
      $rootScope.$on('userStatusChange', decoratedFunction);
      return decoratedFunction;
    };

    init();

    return {
      authWrap: authWrap,
      isAuthenticatedUser: isAuthenticatedUser
    };
  });

}(window.angular));
