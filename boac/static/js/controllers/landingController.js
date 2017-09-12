(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authFactory, me, $scope) {

    $scope.me = me;

    $scope.devAuth = {
      uid: null,
      password: null
    };

    $scope.devAuthLogIn = function() {
      authFactory.devAuthLogIn($scope.devAuth.uid, $scope.devAuth.password).then(
        function successCallback(response) {
          if (response.status === 200) {
            authFactory.status().then(function(results) {
              $scope.me = results.data;
              return;
            });
          } else {
            return;
          }
        }
      );
    };

  });

}(window.angular));
