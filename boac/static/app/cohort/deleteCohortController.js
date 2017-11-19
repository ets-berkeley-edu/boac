(function(angular) {

  'use strict';

  angular.module('boac').controller('DeleteCohortController', function($scope, $uibModal) {

    $scope.openDeleteCohortModal = function(cohort) {
      $uibModal.open({
        animation: true,
        ariaLabelledBy: 'confirm-delete-header',
        ariaDescribedBy: 'confirm-delete-body',
        templateUrl: '/static/app/cohort/deleteCohortModal.html',
        controller: 'DeleteCohortModal',
        resolve: {
          cohort: function() {
            return cohort;
          }
        }
      });
    };
  });

  angular.module('boac').controller('DeleteCohortModal', function(cohort, cohortFactory, $scope, $uibModalInstance) {

    $scope.cohort = cohort;

    $scope.delete = function(item) {
      cohortFactory.deleteCohort(item);
      $uibModalInstance.close();
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
