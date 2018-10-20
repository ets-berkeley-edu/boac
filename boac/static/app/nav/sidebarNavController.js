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
    $rootScope,
    $scope,
    authService,
    config
  ) {
    var init = function() {
      var me = authService.getMe();
      $scope.demoMode = config.demoMode;
      $scope.myFilteredCohorts = _.clone(me.myFilteredCohorts);
      $scope.myCuratedCohorts = _.clone(me.myCuratedCohorts);
      $scope.isAscUser = authService.isAscUser();
    };

    init();

    $rootScope.$on('filteredCohortCreated', function(event, data) {
      $scope.myFilteredCohorts.push(data.cohort);
    });

    $rootScope.$on('filteredCohortDeleted', function(event, data) {
      $scope.myFilteredCohorts = _.remove($scope.myFilteredCohorts, function(curatedCohort) {
        return curatedCohort && (curatedCohort.id !== data.cohort.id);
      });
    });

    $rootScope.$on('filteredCohortUpdated', function(event, data) {
      _.each($scope.myFilteredCohorts, function(cohort) {
        if (cohort.id === data.cohort.id) {
          cohort.name = data.cohort.name;
          cohort.totalStudentCount = data.cohort.totalStudentCount;
        }
      });
    });

    $rootScope.$on('curatedCohortCreated', function(event, data) {
      $scope.myCuratedCohorts.push(data.cohort);
    });

    $rootScope.$on('curatedCohortRenamed', function(event, data) {
      _.each($scope.myCuratedCohorts, function(cohort) {
        if (data.cohort.id === cohort.id) {
          cohort.name = data.cohort.name;
        }
      });
    });

    $rootScope.$on('curatedCohortDeleted', function(event, data) {
      $scope.myCuratedCohorts = _.remove($scope.myCuratedCohorts, function(curatedCohort) {
        return data.cohortId !== curatedCohort.id;
      });
    });

    $rootScope.$on('addStudentToCuratedCohort', function(event, data) {
      var cohort = _.find($scope.myCuratedCohorts, ['id', data.cohort.id]);
      var student = data.student;

      if (!_.find(cohort.students, {sid: student.sid})) {
        cohort.students = _.union(cohort.students, [ student ]);
        cohort.studentCount += 1;
      }
    });

    $rootScope.$on('removeStudentFromCuratedCohort', function(event, data) {
      var curatedCohort = _.find($scope.myCuratedCohorts, ['id', data.cohort.id]);
      curatedCohort.studentCount -= 1;
    });
  });

}(window.angular));
