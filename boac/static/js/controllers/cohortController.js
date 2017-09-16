(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(cohortFactory, $scope, $stateParams) {

    cohortFactory.getCohortDetails($stateParams.code).then(function(cohort) {
      $scope.cohort = cohort.data;
    });

  });

}(window.angular));
