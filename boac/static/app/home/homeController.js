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

  angular.module('boac').controller('HomeController', function(
    $scope,
    authService,
    curatedCohortFactory,
    filteredCohortFactory,
    page,
    utilService
  ) {

    var decorateCohort = function(cohort, students) {
      _.each(students, function(student) {
        student.alertCount = student.alertCount || 0;
        student.term = student.term || {};
        student.term.enrolledUnits = student.term.enrolledUnits || 0;
      });
      _.assignIn(cohort, {
        alertCount: _.sum(_.map(students, 'alertCount')),
        sortOptions: {
          reverse: false,
          sortBy: 'sortableName'
        },
        students: utilService.extendSortableNames(students)
      });
    };

    $scope.clickCuratedCohort = function(cohort) {
      if (_.isNil(cohort.students)) {
        var done = function() {
          cohort.isLoading = false;
          cohort.isOpen = !cohort.isOpen;
        };
        cohort.isLoading = true;
        if (cohort.studentCount) {
          curatedCohortFactory.getStudentsWithAlertsInCohort(cohort.id).then(function(response) {
            decorateCohort(cohort, response.data);
            done();
          });
        } else {
          done();
        }
      } else {
        cohort.isOpen = !cohort.isOpen;
      }
    };

    $scope.clickFilteredCohort = function(cohort) {
      if (_.isNil(cohort.students)) {
        var done = function() {
          cohort.isLoading = false;
          cohort.isOpen = !cohort.isOpen;
        };
        cohort.isLoading = true;
        if (cohort.totalStudentCount) {
          filteredCohortFactory.getStudentsWithAlertsInCohort(cohort.id).then(function(response) {
            decorateCohort(cohort, response.data);
            done();
          });
        } else {
          done();
        }
      } else {
        cohort.isOpen = !cohort.isOpen;
      }
    };

    var init = function() {
      authService.loadUserProfile().then(function(profile) {
        $scope.profile = profile;
        page.loading(false);
      });
    };

    page.loading(true);
    init();
  });

}(window.angular));
