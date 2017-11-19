(function(angular) {

  'use strict';

  angular.module('boac').controller('ManageCohortsController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = true;

    var resetPageView = function(callback) {
      // For each cohort listed in the UI, hide details and the edit form
      _.each($scope.myCohorts, function(next) {
        next.editMode = false;
        next.detailsShowing = false;
      });
      return callback();
    };

    var setEditMode = $scope.setEditMode = function(cohort, newValue) {
      resetPageView(function() {
        cohort.detailsShowing = newValue;
        cohort.editMode = newValue;
      });
    };

    $scope.setShowDetails = function(cohort, newValue) {
      resetPageView(function() {
        cohort.detailsShowing = newValue;
      });
    };

    $scope.updateCohort = function(cohort, label) {
      cohortFactory.updateCohort(cohort.id, label).then(function() {
        setEditMode(cohort, false);
      });
    };

    $scope.deleteCohort = cohortFactory.deleteCohort;

    var init = function() {
      $scope.isLoading = true;

      cohortFactory.getMyCohorts().then(function(response) {
        $scope.myCohorts = response.data;
        resetPageView(angular.noop);

        $scope.isLoading = false;
      });
    };

    $rootScope.$on('myCohortsUpdated', init);

    authService.authWrap(init)();
  });

}(window.angular));
