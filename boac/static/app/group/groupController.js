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

  angular.module('boac').controller('GroupController', function(
    config,
    studentGroupFactory,
    studentSearchService,
    utilService,
    validationService,
    visualizationService,
    $location,
    $scope,
    $stateParams
  ) {

    $scope.orderBy = studentSearchService.getSortByOptionsForSearch();

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
        // group_name here refers to team groups (i.e., athletic memberships) and not the user-created groups you'd expect.
        case 'group_name':
          return _.get(student, 'athletics[0].groupName');
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

    var goToStudent = $scope.goToStudent = function(uid) {
      utilService.goTo('/student/' + uid, $scope.group.name);
    };

    /**
     * @param  {Function}    callback      Standard callback function
     * @return {void}
     */
    var matrixViewRefresh = function(callback) {
      $scope.isLoading = true;
      var goToUserPage = function(uid) {
        $location.state($location.absUrl());
        goToStudent(uid);
        // The intervening visualizationService code moves out of Angular and into d3 thus the extra kick of $apply.
        $scope.$apply();
      };
      visualizationService.scatterplotRefresh($scope.group.students, goToUserPage, function(yAxisMeasure, studentsWithoutData) {
        $scope.yAxisMeasure = yAxisMeasure;
        // List of students-without-data is rendered below the scatterplot.
        $scope.studentsWithoutData = studentsWithoutData;
      });
      return callback();
    };

    /**
     * @param  {String}    tabName          Name of tab clicked by user
     * @return {void}
     */
    var onTab = $scope.onTab = function(tabName) {
      $scope.tab = tabName;
      $location.search('v', $scope.tab);
      // Lazy load matrix data
      if (tabName === 'matrix') {
        matrixViewRefresh(function() {
          $scope.isLoading = false;
        });
      } else if (tabName === 'list') {
        // Do nothing.
      }
    };

    $scope.removeFromGroup = function(student) {
      studentGroupFactory.removeStudentFromGroup($scope.group.id, student).then(function() {
        $scope.group.students = _.remove($scope.group.students, function(s) {
          return s.sid !== student.sid;
        });
      });
    };

    var init = function() {
      $scope.isLoading = true;
      var id = $stateParams.id;
      var args = _.clone($location.search());

      studentGroupFactory.getGroup(id).then(function(response) {
        $scope.group = response.data;
        onTab(_.includes(['list', 'matrix'], args.v) ? args.v : 'list');
        $scope.isLoading = false;
      }).catch(function(err) {
        $scope.error = validationService.parseError(err);
      });
    };

    init();
  });

}(window.angular));
