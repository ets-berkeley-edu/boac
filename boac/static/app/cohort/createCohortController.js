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

  angular.module('boac').controller('CreateCohortModal', function(teamGroups, cohortFactory, $rootScope, $scope, $uibModalInstance) {

    $scope.cohortName = null;
    $scope.errorMessage = null;

    $scope.create = function() {
      $scope.cohortName = _.trim($scope.cohortName);
      if (_.isEmpty($scope.cohortName)) {
        $scope.errorMessage = 'Required';
      } else {
        $rootScope.isSaving = true;

        var selectedTeamGroups = _.filter(teamGroups, 'selected');
        cohortFactory.createCohort($scope.cohortName, _.map(selectedTeamGroups, 'teamGroupCode')).then(function() {
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
