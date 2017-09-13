(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authFactory, config, $scope) {

    $scope.devAuthEnabled = config.devAuthEnabled;

    $scope.devAuth = {
      uid: null,
      password: null
    };

    $scope.devAuthLogIn = function() {
      return authFactory.devAuthLogIn($scope.devAuth.uid, $scope.devAuth.password);
    };

    $scope.logOut = authFactory.logOut;
  });

}(window.angular));
