(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = false;

    var loadCohorts = function() {
      if (authService.isAuthenticatedUser()) {
        $scope.isLoading = true;

        cohortFactory.getCohorts().then(function(cohorts) {
          $scope.cohorts = cohorts.data;
          $scope.isLoading = false;
        });
      }
    };

    $rootScope.$on('userStatusChange', loadCohorts);

    $rootScope.$on('authenticationFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    loadCohorts();
  });

}(window.angular));
