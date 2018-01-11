(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = true;
    $scope.isAuthenticated = authService.isAuthenticatedUser();

    var init = function() {
      if ($scope.isAuthenticated) {
        cohortFactory.getTeams().then(function(teamsResponse) {
          $scope.teams = teamsResponse.data;

          cohortFactory.getMyCohorts().then(function(response) {
            $scope.myCohorts = response.data;
            $scope.isLoading = false;
          });
        });
      } else {
        $scope.isLoading = false;
      }
    };

    $rootScope.$on('devAuthFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    init();
  });

}(window.angular));
