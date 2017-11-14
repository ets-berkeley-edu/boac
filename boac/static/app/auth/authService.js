(function(angular) {

  'use strict';

  angular.module('boac').service('authService', function(authFactory, $http, $rootScope) {

    var isAuthenticatedUser = function() {
      return $rootScope.me && $rootScope.me.authenticated_as.is_authenticated;
    };

    var init = function() {
      $http.get('/api/status').then(authFactory.loadUserProfile);
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
