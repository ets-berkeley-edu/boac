/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').controller('CreateGroupController', function($scope, $uibModal) {

    $scope.openCreateCuratedCohortModal = function() {
      var modal = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'create-curated-cohort-header',
        ariaDescribedBy: 'create-curated-cohort-body',
        templateUrl: '/static/app/group/createGroupModal.html',
        controller: 'CreateGroupModal',
        resolve: {}
      });
      modal.result.finally(function() {
        $scope.$destroy();
      }).then(angular.noop, angular.noop);
    };
  });

  angular.module('boac').controller('CreateGroupModal', function(
    studentGroupFactory,
    validationService,
    $scope,
    $uibModalInstance
  ) {
    $scope.name = null;
    $scope.error = {
      hide: false,
      message: null
    };

    $scope.create = function() {
      $scope.isSaving = true;
      // The 'error.hide' flag allows us to hide validation error on-change of form input.
      $scope.error = {
        hide: false,
        message: null
      };
      $scope.name = _.trim($scope.name);
      validationService.validateName({name: $scope.name}, function(errorMessage) {
        if (errorMessage) {
          $scope.isSaving = false;
          $scope.error.message = errorMessage;
        } else {
          // Get values where selected=true
          studentGroupFactory.createGroup($scope.name).then(
            function() {
              $scope.isSaving = false;
              $uibModalInstance.close();
            },
            function(err) {
              $scope.error.message = 'Sorry, the operation failed due to error: ' + err.data.message;
              $scope.isSaving = false;
            }
          );
        }
      });
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
