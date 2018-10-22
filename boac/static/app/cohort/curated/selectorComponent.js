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

  var CuratedCohortSelector = function($rootScope, $scope, $timeout, curatedCohortFactory, page) {

    page.loading(true);

    $scope.selector = {
      selectAllCheckbox: false,
      showCuratedCohortMenu: false
    };

    /**
     * Show or hide the curated cohorts menu based on page state.
     *
     * @return {void}
     */
    var updateCuratedCohortMenu = function() {
      $scope.selector.showCuratedCohortMenu = $scope.selector.selectAllCheckbox || !!_.find($scope.students, 'selectedForCuratedCohort');
    };

    var initStudent = function(student) {
      // Init all student checkboxes to false
      student.selectedForCuratedCohort = false;
      student.curatedCohortToggle = function(event) {
        event.stopPropagation();
        student.selectedForCuratedCohort = !student.selectedForCuratedCohort;

        if (student.selectedForCuratedCohort) {
          $scope.selector.showCuratedCohortMenu = true;
          var selectAllCheckbox = true;

          _.each($scope.students, function(s) {
            if (!s.selectedForCuratedCohort) {
              // We found a checkbox not checked. The 'all' checkbox must be false.
              selectAllCheckbox = false;
              // Break out of loop.
              return false;
            }
          });
          $scope.selector.selectAllCheckbox = selectAllCheckbox;
        } else {
          $scope.selector.selectAllCheckbox = false;
        }
      };
    };

    /**
     * Toggle the curated cohort checkbox.
     *
     * @param  {Boolean}    value      If true, select all students in current page view.
     * @return {void}
     */
    var toggleAllStudentCheckboxes = $scope.toggleAllStudentCheckboxes = function(value) {
      var selected = _.isNil(value) ? !$scope.selector.selectAllCheckbox : value;
      _.each($scope.students, function(student) {
        student.selectedForCuratedCohort = selected;
      });
      $scope.selector.selectAllCheckbox = selected;
      updateCuratedCohortMenu();
      $scope.selector.showCuratedCohortMenu = selected;
    };

    var deselect = function(option) {
      _.set(option, 'selected', false);
    };

    /**
     * Add selected students to the curated cohort provided and then reset all curated-cohort related menus.
     *
     * @param  {Object}    cohort      Students will be added to this cohort.
     * @return {void}
     */
    $scope.curatedCohortCheckboxClick = function(cohort) {
      $scope.isSaving = true;
      var students = _.filter($scope.students, function(student) {
        return student.selectedForCuratedCohort && !_.find(cohort.students, {sid: student.sid});
      });
      curatedCohortFactory.addStudents(cohort.id, _.map(students, 'sid')).then(function() {
        $scope.selector.selectAllCheckbox = false;
        _.each($scope.students, function(student) {
          student.selectedForCuratedCohort = false;
        });
      }).finally(function() {
        $scope.selector.selectAllCheckbox = false;
        $timeout(function() {
          _.each($scope.profile.myCuratedCohorts, deselect);
          toggleAllStudentCheckboxes(false);
          $scope.isSaving = false;
        }, 2000);
      });
    };

    this.$onInit = function() {
      $scope.profile = $rootScope.profile;
      $scope.students = this.students;
      _.each($scope.profile.myCuratedCohorts, deselect);
      _.each($scope.students, initStudent);
      page.loading(false);
    };

    $rootScope.$on('resetCuratedCohortSelector', function() {
      toggleAllStudentCheckboxes(false);
    });
  };

  angular.module('boac').component('curatedCohortSelector', {
    bindings: {
      students: '='
    },
    controller: CuratedCohortSelector,
    templateUrl: '/static/app/cohort/curated/selector.html'
  });

}(window.angular));
