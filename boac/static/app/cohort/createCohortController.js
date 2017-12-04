(function(angular) {

  'use strict';

  angular.module('boac').controller('CreateCohortController', function($scope, $uibModal) {

    $scope.openCreateCohortModal = function(teams) {
      $uibModal.open({
        animation: true,
        ariaLabelledBy: 'create-cohort-header',
        ariaDescribedBy: 'create-cohort-body',
        templateUrl: '/static/app/cohort/createCohortModal.html',
        controller: 'CreateCohortModal',
        resolve: {
          teams: function() {
            return teams;
          }
        }
      });
    };
  });

  angular.module('boac').controller('CreateCohortModal', function(teams, cohortFactory, $rootScope, $scope, $uibModalInstance) {

    $scope.cohortName = null;
    $scope.errorMessage = null;

    $scope.create = function() {
      $scope.cohortName = _.trim($scope.cohortName);
      if (_.isEmpty($scope.cohortName)) {
        $scope.errorMessage = 'Required';
      } else {
        $rootScope.isSaving = true;

        var selectedTeams = _.filter(teams, 'selected');
        cohortFactory.createCohort($scope.cohortName, _.map(selectedTeams, 'code')).then(function() {
          $rootScope.isSaving = false;
        });
        $uibModalInstance.close();
      }
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
