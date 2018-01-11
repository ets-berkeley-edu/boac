(function(angular) {

  'use strict';

  angular.module('boac').controller('AllCohortsController', function(cohortFactory, $scope) {

    $scope.isLoading = true;
    $scope.isEmpty = _.isEmpty;

    var init = function() {
      cohortFactory.getAll().then(function(allResponse) {
        $scope.allCohorts = allResponse.data;
        $scope.isLoading = false;
      });
    };

    init();
  });

}(window.angular));
