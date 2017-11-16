(function(angular) {

  'use strict';

  angular.module('boac').controller('ManageCohortsController', function(authService, cohortFactory, $scope) {

    $scope.isLoading = true;

    $scope.updateCohort = cohortFactory.updateCohort;
    $scope.deleteCohort = cohortFactory.deleteCohort;

    var init = function() {
      $scope.isLoading = true;

      cohortFactory.getMyCohorts().then(function(response) {
        $scope.myCohorts = response.data;
        $scope.isLoading = false;
      });
    };

    authService.authWrap(init)();
  });

}(window.angular));
