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

  angular.module('boac').controller('DeleteCohortController', function($scope, $uibModal) {

    var isModalOpen = false;

    $scope.openDeleteCohortModal = function(cohort, stateAfterDelete) {
      if (isModalOpen) {
        return;
      }
      isModalOpen = true;

      var modal = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'confirm-delete-header',
        ariaDescribedBy: 'confirm-delete-body',
        backdrop: false,
        templateUrl: '/static/app/cohort/filtered/deleteModal.html',
        controller: 'DeleteCohortModal',
        resolve: {
          cohort: function() {
            return cohort;
          },
          stateAfterDelete: function() {
            return stateAfterDelete;
          }
        }
      });
      var modalClosed = function() {
        isModalOpen = false;
      };

      modal.result.finally(angular.noop).then(modalClosed, modalClosed);
    };
  });

  angular.module('boac').controller('DeleteCohortModal', function(
    $scope,
    $uibModalInstance,
    cohort,
    filteredCohortFactory,
    stateAfterDelete,
    validationService
  ) {

    $scope.cohort = cohort;

    $scope.delete = function(item) {
      filteredCohortFactory.deleteCohort(item).then(function() {
        if (stateAfterDelete) {
          $state.go(stateAfterDelete);
        } else {
          $uibModalInstance.close();
        }
      }).catch(function(error) {
        $scope.error = validationService.parseError(error);
      });
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
