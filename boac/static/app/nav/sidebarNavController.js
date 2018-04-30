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

  angular.module('boac').controller('SidebarNavController', function(
    authService,
    cohortService,
    config,
    studentGroupFactory,
    studentGroupService,
    $rootScope,
    $scope,
    $state
  ) {
    var init = function() {
      var me = authService.getMe();
      $scope.demoMode = config.demoMode;
      $scope.myCohorts = _.clone(me.myCohorts);
      $scope.myGroups = _.clone(me.myGroups);
      $scope.searchPhrase = null;
      $scope.showAthletics = me.isAdmin || authService.isCurrentUserAscAdvisor();
    };

    init();

    $rootScope.$on('$viewContentLoaded', function() {
      $scope.searchPhrase = null;
    });

    $scope.searchForStudents = function() {
      $scope.searchResultsLoading = true;
      $state.transitionTo('search', {q: $scope.searchPhrase}, {reload: true});
    };

    var findGroupInScope = function(groupId) {
      return _.find($scope.myGroups, ['id', groupId]);
    };

    $rootScope.$on('cohortCreated', function(event, data) {
      var cohort = data.cohort;
      cohortService.decorateCohortAlerts(cohort);
      $scope.myCohorts.push(cohort);
    });

    $rootScope.$on('cohortDeleted', function(event, data) {
      $scope.myCohorts = _.remove($scope.myCohorts, function(cohort) {
        return cohort && (cohort.id !== data.cohort.id);
      });
    });

    $rootScope.$on('cohortNameChanged', function(event, data) {
      _.each($scope.myCohorts, function(cohort) {
        if (cohort.id === data.cohort.id) {
          cohort.label = data.cohort.label;
        }
      });
    });

    $rootScope.$on('groupCreated', function(event, data) {
      $scope.myGroups.push(data.group);
    });

    $rootScope.$on('groupNameChanged', function(event, data) {
      _.each($scope.myGroups, function(group) {
        if (data.group.id === group.id) {
          group.name = data.group.name;
        }
      });
    });

    $rootScope.$on('groupDeleted', function(event, data) {
      $scope.myGroups = _.remove($scope.myGroups, function(group) {
        return data.groupId !== group.id;
      });
    });

    $rootScope.$on('addStudentToGroup', function(event, data) {
      var group = findGroupInScope(data.group.id);
      var student = data.student;

      if (!studentGroupService.isStudentInGroup(student, group)) {
        student.name = student.name || student.athleticsProfile.fullName;
        group.students = _.union(group.students, [ student ]);
        group.studentCount += 1;
      }
    });

    $rootScope.$on('removeStudentFromGroup', function(event, data) {
      var group = findGroupInScope(data.group.id);
      var student = data.student;

      if (studentGroupService.isStudentInGroup(student, group)) {
        group.students = _.remove(group.students, function(s) {
          return s.sid !== student.sid;
        });
        group.studentCount -= 1;
      }
    });
  });

}(window.angular));
