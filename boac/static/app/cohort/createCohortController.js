(function(angular) {

  'use strict';

  angular.module('boac').controller('CreateCohortController', function($scope, $uibModal) {

    $scope.openCreateCohortModal = function(teamGroups) {
      $uibModal.open({
        animation: true,
        ariaLabelledBy: 'create-cohort-header',
        ariaDescribedBy: 'create-cohort-body',
        templateUrl: '/static/app/cohort/createCohortModal.html',
        controller: 'CreateCohortModal',
        resolve: {
          teamGroups: function() {
            return teamGroups;
          }
        }
      });
    };
  });

  angular.module('boac').controller('CreateCohortModal', function(teamGroups, cohortFactory, cohortService, $rootScope, $scope, $uibModalInstance) {

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
            var selectedTeamGroups = _.filter(teamGroups, 'selected');
            cohortFactory.createCohort($scope.label, _.map(selectedTeamGroups, 'groupCode')).then(function() {
              $rootScope.isSaving = false;
              $uibModalInstance.close();
            });
          }
        });
      }
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
