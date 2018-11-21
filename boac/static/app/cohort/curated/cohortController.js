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

  angular.module('boac').controller('CuratedCohortController', function(
    $location,
    $rootScope,
    $scope,
    $state,
    $stateParams,
    authService,
    cohortService,
    config,
    curatedCohortFactory,
    page,
    status,
    utilService,
    validationService
  ) {

    $scope.cohortId = _.toNumber($stateParams.id);
    $scope.currentEnrollmentTerm = config.currentEnrollmentTerm;
    $scope.inDemoMode = status.inDemoMode;
    $scope.isAscUser = authService.isAscUser();
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.orderBy = cohortService.getSortByOptionsForSearch();

    var levelComparator = function(level) {
      switch (level) {
        case 'Freshman':
          return 1;
        case 'Sophomore':
          return 2;
        case 'Junior':
          return 3;
        case 'Senior':
          return 4;
        default:
          return 0;
      }
    };

    $scope.studentComparator = function(student) {
      switch ($scope.orderBy.selected) {
        case 'first_name':
          return student.firstName;
        case 'last_name':
          return student.lastName;
        // group_name here refers to team groups (i.e., athletic memberships) and not the user-created cohorts you'd expect.
        case 'group_name':
          return _.get(student, 'athleticsProfile.athletics[0].groupName');
        case 'gpa':
          return student.cumulativeGPA;
        case 'level':
          return levelComparator(student.level);
        case 'major':
          return _.get(student, 'majors[0]');
        case 'units':
          return student.cumulativeUnits;
        default:
          return '';
      }
    };

    var errorHandler = function(error) {
      if (error.status === 404) {
        $location.replace().path('/404');
      } else {
        $scope.error = validationService.parseError(error);
        page.loading(false);
        return $scope.error;
      }
    };

    $scope.renameMode = {
      error: null,
      input: null,
      on: false
    };

    $scope.enterRenameMode = function(originalName) {
      $scope.renameMode.input = originalName;
      $scope.renameMode.on = true;
    };

    var exitRenameMode = $scope.exitRenameMode = function() {
      $scope.renameMode.on = false;
      $scope.renameMode.input = null;
    };

    $scope.rename = function($event) {
      $event.stopPropagation();
      var name = $scope.renameMode.input;
      validationService.validateName({id: $scope.cohortId, name: name}, function(error) {
        if (error) {
          $scope.renameMode.error = errorHandler(error);
        } else {
          curatedCohortFactory.rename($scope.cohortId, name).then(function() {
            $scope.cohortName = $scope.cohort.name = name;
            exitRenameMode();
          }).catch(errorHandler);
        }
      });
    };

    $scope.removeFromCuratedCohort = function(student) {
      curatedCohortFactory.removeStudent($scope.cohortId, student.sid).then(function() {
        $scope.students = _.remove($scope.students, function(s) {
          return s.sid !== student.sid;
        });
      });
    };

    $scope.callbacks = {
      onDelete: function() {
        $state.go('home');
      }
    };

    var init = function() {
      page.loading(true);
      curatedCohortFactory.getCuratedCohort($scope.cohortId).then(function(response) {
        $scope.cohort = response.data;
        $scope.cohortName = $rootScope.pageTitle = $scope.cohort.name || 'Curated Group';
        $scope.students = $scope.cohort.students;
        page.loading(false);
      }).catch(function(err) {
        $scope.error = validationService.parseError(err);
      });
    };

    init();
  });

}(window.angular));
