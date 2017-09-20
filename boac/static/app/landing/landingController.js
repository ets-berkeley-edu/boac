(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(cohortFactory, $scope) {

    cohortFactory.getCohorts().then(function(cohorts) {
      $scope.cohorts = cohorts.data;
    });

  });

}(window.angular));
