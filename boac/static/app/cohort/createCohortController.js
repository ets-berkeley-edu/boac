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
              cohortService.getSelected(filters.gpaRanges, 'value'),
              cohortService.getSelected(filters.teamGroups, 'groupCode'),
              cohortService.getSelected(filters.levels, 'name'),
              cohortService.getSelected(filters.majors, 'name'),
              cohortService.getSelected(filters.unitRanges, 'value')
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
