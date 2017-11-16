(function(angular) {

  'use strict';

  angular.module('boac').controller('AllCohortsController', function(authService, cohortFactory, $scope) {

    $scope.isLoading = true;
    $scope.isEmpty = _.isEmpty;

    var init = function() {
      cohortFactory.getAll().then(function(allResponse) {
        $scope.allCohorts = allResponse.data;
        $scope.isLoading = false;
      });
    };

    authService.authWrap(init)();
  });

}(window.angular));
