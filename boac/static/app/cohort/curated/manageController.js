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

  angular.module('boac').controller('ManageCuratedCohortsController', function(
    $rootScope,
    $scope,
    curatedCohortFactory,
    validationService
  ) {

    $scope.profile = $rootScope.profile;

    var resetPageView = function(callback) {
      _.each($scope.cohorts, function(cohort) {
        cohort.editMode = false;
      });
      return callback();
    };

    var setEditMode = $scope.setEditMode = function(cohort, newValue) {
      resetPageView(function() {
        cohort.editMode = newValue;
      });
    };

    $scope.cancelEdit = function(cohort) {
      cohort.name = cohort.nameOriginal;
      setEditMode(cohort, false);
    };

    $scope.rename = function(cohort, name) {
      validationService.validateName({id: cohort.id, name: name}, function(error) {
        cohort.error = error;
        cohort.hideError = false;
        if (!cohort.error) {
          curatedCohortFactory.rename(cohort.id, name).then(function() {
            cohort.nameOriginal = name;
            setEditMode(cohort, false);
          });
        }
      });
    };

    /**
     * @return {void}
     */
    var init = function() {
      _.each($rootScope.profile.myCuratedCohorts, function(cohort) {
        cohort.nameOriginal = cohort.name;
      });
      resetPageView(angular.noop);
    };

    init();
  });

}(window.angular));
