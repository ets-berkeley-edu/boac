(function(angular) {

  'use strict';

  angular.module('boac').controller('AllCohortsController', function(cohortFactory, $scope) {

    $scope.isLoading = true;

    var init = function() {
      cohortFactory.getAll().then(function(response) {
        $scope.owners = response.data;
        $scope.isLoading = false;
      });
    };

    init();
  });

}(window.angular));
