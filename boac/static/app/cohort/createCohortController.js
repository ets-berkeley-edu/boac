(function(angular) {

  'use strict';

  angular.module('boac').controller('CreateCohortController', function($scope, $uibModal) {

    $scope.openCreateCohortModal = function(filters) {
      $uibModal.open({
        animation: true,
        ariaLabelledBy: 'create-cohort-header',
        ariaDescribedBy: 'create-cohort-body',
        templateUrl: '/static/app/cohort/createCohortModal.html',
        controller: 'CreateCohortModal',
        resolve: {
          filters: function() {
            return filters;
          }
        }
      });
    };
  });

  angular.module('boac').controller('CreateCohortModal', function(filters, cohortFactory, cohortService, $rootScope, $scope, $uibModalInstance) {

    // If we use the name '$scope.cohort' then we will collide with model name of underlying /cohort view.
    $scope.label = null;
    $scope.error = {
      hide: false,
      message: null
    };

    var getSelected = function(filterOptions, property) {
      return _.map(_.filter(filterOptions, 'selected'), property);
    };

    $scope.create = function() {
      // The 'error.hide' flag allows us to hide validation error on-change of form input.
      $scope.error.hide = false;
      $scope.label = _.trim($scope.label);
      if (_.isEmpty($scope.label)) {
        $scope.error.message = 'Required';
      } else if (_.size($scope.label) > 255) {
        $scope.error.message = 'Name must be 255 characters or fewer';
      } else {
        cohortService.validateCohortLabel({label: $scope.label}, function(errorMessage) {
          $scope.error.message = errorMessage;
          if (!$scope.error.message) {
            $rootScope.isSaving = true;
            cohortFactory.createCohort(
              $scope.label,
              getSelected(filters.gpaRanges, 'name'),
              getSelected(filters.teamGroups, 'groupCode'),
              getSelected(filters.levels, 'name'),
              getSelected(filters.majors, 'name'),
              getSelected(filters.unitRangesEligibility, 'name'),
              getSelected(filters.unitRangesPacing, 'name')
            ).then(
              function() {
                $rootScope.isSaving = false;
                $uibModalInstance.close();
              },
              function(err) {
                $scope.error.message = 'Sorry, the operation failed due to error: ' + err.data.message;
                $rootScope.isSaving = false;
              }
            );
          }
        });
      }
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
