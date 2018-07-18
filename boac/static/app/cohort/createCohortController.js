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

  angular.module('boac').controller('CreateCohortController', function($scope, $uibModal) {

    var isModalOpen = false;

    $scope.openCreateCohortModal = function(opts) {
      if (isModalOpen) {
        return;
      }
      isModalOpen = true;

      var modal = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'create-filtered-cohort-header',
        ariaDescribedBy: 'create-filtered-cohort-body',
        backdrop: false,
        templateUrl: '/static/app/cohort/createCohortModal.html',
        controller: 'CreateCohortModal',
        resolve: {
          opts: function() {
            return opts;
          }
        }
      });
      var modalClosed = function() {
        isModalOpen = false;
      };

      modal.result.finally(angular.noop).then(modalClosed, modalClosed);
    };
  });

  angular.module('boac').controller('CreateCohortModal', function(
    opts,
    cohortFactory,
    utilService,
    validationService,
    $rootScope,
    $scope,
    $uibModalInstance
  ) {
    $scope.label = null;
    $scope.error = {
      hide: false,
      message: null
    };
    $scope.create = function() {
      $rootScope.isSaving = true;
      // The 'error.hide' flag allows us to hide validation error on-change of form input.
      $scope.error = {
        hide: false,
        message: null
      };
      $scope.label = _.trim($scope.label);
      validationService.validateName({name: $scope.label}, function(errorMessage) {
        if (errorMessage) {
          $scope.error.message = errorMessage;
          $rootScope.isSaving = false;
        } else {
          var getValues = utilService.getValuesSelected;
          // Get values where selected=true
          cohortFactory.createCohort(
            $scope.label,
            opts.advisorLdapUid,
            getValues(opts.gpaRanges),
            getValues(opts.groupCodes, 'groupCode'),
            getValues(opts.levels),
            getValues(opts.majors),
            getValues(opts.unitRanges),
            opts.intensive,
            opts.inactive
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
    };

    $scope.cancel = function() {
      $uibModalInstance.close();
    };
  });

}(window.angular));
