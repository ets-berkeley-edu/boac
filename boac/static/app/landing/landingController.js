(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(cohortFactory, $rootScope, $scope) {

    var loadCohorts = function() {
      cohortFactory.getCohorts().then(function(cohorts) {
        $scope.cohorts = cohorts.data;
      });
    };

    /**
     * Refresh
     */
    $rootScope.$on('authenticationSuccess', function() {
      loadCohorts();
    });

    /**
     * Refresh
     */
    $rootScope.$on('authenticationFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    loadCohorts();
  });

}(window.angular));
