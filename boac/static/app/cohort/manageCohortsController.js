(function(angular) {

  'use strict';

  angular.module('boac').controller('ManageCohortsController', function(
    authService,
    cohortFactory,
    cohortService,
    studentFactory,
    utilService,
    $rootScope,
    $scope
  ) {

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

    var names = function(cohortCriteria, allOptions, propertyName) {
      var gpaRanges = _.filter(allOptions, function(option) {
        return _.includes(cohortCriteria, option.value);
      });
      return _.map(gpaRanges, propertyName);
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

    /**
     * @return {void}
     */
    var init = function() {
      cohortFactory.getMyCohorts().then(function(response) {
        $scope.myCohorts = response.data;
        _.each($scope.myCohorts, function(cohort) {
          cohort.labelOriginal = cohort.label;

          var f = cohort.filterCriteria;
          cohort.filterCriteriaNames = _.concat(
            _.map(names(f.gpaRanges, studentFactory.getGpaRanges(), 'name'), function(name) {
              return 'GPA: ' + name;
            }),
            _.map(cohort.teamGroups, 'groupName'),
            _.map(f.levels, function(level) { return 'Level: ' + level; }),
            _.map(f.majors, function(major) { return 'Major: ' + major; }),
            _.map(names(f.unitRanges, studentFactory.getUnitRanges(), 'name'), function(name) {
              return 'Units: ' + name;
            })
          );
        });
        resetPageView(angular.noop);
        $scope.isLoading = false;
      });
    };

    $rootScope.$on('cohortDeleted', function(event, data) {
      $scope.myCohorts = $scope.myCohorts = _.remove($scope.myCohorts, function(c) {
        return c.id !== data.cohort.id;
      });
    });

    init();
  });

}(window.angular));
