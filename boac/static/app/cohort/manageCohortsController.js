(function(angular) {

  'use strict';

  angular.module('boac').controller('ManageCohortsController', function(authService, cohortFactory, cohortService, utilService, $rootScope, $scope) {

    $scope.truncate = utilService.truncate;
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

    $scope.cancelEdit = function(cohort) {
      cohort.label = cohort.labelOriginal;
      setEditMode(cohort, false);
    };

    $scope.updateCohort = function(cohort, label) {
      cohortService.validateCohortLabel({id: cohort.id, label: label}, function(error) {
        cohort.error = error;
        cohort.hideError = false;
        if (!cohort.error) {
          cohortFactory.updateCohort(cohort.id, label).then(function() {
            cohort.labelOriginal = label;
            setEditMode(cohort, false);
          });
        }
      });
    };

    $scope.deleteCohort = cohortFactory.deleteCohort;

    var init = function() {
      cohortFactory.getMyCohorts().then(function(response) {
        $scope.myCohorts = response.data;
        _.each($scope.myCohorts, function(cohort) {
          cohort.labelOriginal = cohort.label;
        });
        resetPageView(angular.noop);

        $scope.isLoading = false;
      });
    };

    $rootScope.$on('myCohortsUpdated', init);

    authService.authWrap(init)();
  });

}(window.angular));
