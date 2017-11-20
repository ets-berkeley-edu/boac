(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = true;

    var init = function() {
      cohortFactory.getTeams().then(function(teamsResponse) {
        $scope.teams = teamsResponse.data;

        cohortFactory.getMyCohorts().then(function(response) {
          $scope.myCohorts = response.data;
          $scope.isLoading = false;
        });
      });
    };

    $rootScope.$on('authenticationFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    authService.authWrap(init)();
  });

}(window.angular));
