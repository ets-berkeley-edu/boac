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

  angular.module('boac').controller('ManageCohortsController', function(
    authService,
    cohortFactory,
    cohortService,
    studentFactory,
    utilService,
    $rootScope,
    $scope
  ) {

    $scope.truncate = utilService.truncate;
    $scope.isLoading = true;

    var resetPageView = function(callback) {
      // For each cohort listed in the UI, hide details and the edit form
      _.each($scope.myCohorts, function(next) {
        next.editMode = false;
        next.detailsShowing = false;
      });
      return callback();
    };

    var names = function(cohortCriteria, allOptions, propertyName) {
      var gpaRanges = _.filter(allOptions, function(option) {
        return _.includes(cohortCriteria, option.value);
      });
      return _.map(gpaRanges, propertyName);
    };

    var setEditMode = $scope.setEditMode = function(cohort, newValue) {
      resetPageView(function() {
        cohort.detailsShowing = newValue;
        cohort.editMode = newValue;
      });
    };

    $scope.setShowDetails = function(cohort, newValue) {
      resetPageView(function() {
        cohort.detailsShowing = newValue;
      });
    };

    $scope.cancelEdit = function(cohort) {
      cohort.label = cohort.labelOriginal;
      setEditMode(cohort, false);
    };

    $scope.updateCohort = function(cohort, label) {
      cohortService.validateCohortLabel({id: cohort.id, label: label}, function(error) {
        cohort.error = error;
        cohort.hideError = false;
        if (!cohort.error) {
          cohortFactory.updateCohort(cohort.id, label).then(function() {
            cohort.labelOriginal = label;
            setEditMode(cohort, false);
          });
        }
      });
    };

    $scope.deleteCohort = cohortFactory.deleteCohort;

    /**
     * @return {void}
     */
    var init = function() {
      cohortFactory.getMyCohorts().then(function(response) {
        $scope.myCohorts = response.data;
        _.each($scope.myCohorts, function(cohort) {
          cohort.labelOriginal = cohort.label;

          var f = cohort.filterCriteria;
          cohort.filterCriteriaNames = _.concat(
            _.map(names(f.gpaRanges, studentFactory.getGpaRanges(), 'name'), function(name) {
              return 'GPA: ' + name;
            }),
            _.map(cohort.teamGroups, 'groupName'),
            _.map(f.levels, function(level) { return 'Level: ' + level; }),
            _.map(f.majors, function(major) { return 'Major: ' + major; }),
            _.map(names(f.unitRanges, studentFactory.getUnitRanges(), 'name'), function(name) {
              return 'Units: ' + name;
            }),
            f.inIntensiveCohort ? [ 'Intensive' ] : []
          );
        });
        resetPageView(angular.noop);
        $scope.isLoading = false;
      });
    };

    $rootScope.$on('cohortDeleted', function(event, data) {
      $scope.myCohorts = $scope.myCohorts = _.remove($scope.myCohorts, function(c) {
        return c.id !== data.cohort.id;
      });
    });

    init();
  });

}(window.angular));
