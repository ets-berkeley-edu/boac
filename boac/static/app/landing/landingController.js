(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = true;

    var init = function() {
      cohortFactory.getTeams().then(function(response) {
        $scope.teams = response.data;
        $scope.isLoading = false;
      });
    };

    $rootScope.$on('authenticationFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    authService.authWrap(init)();
  });

}(window.angular));
