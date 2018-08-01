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

  angular.module('boac').controller('StudentController', function(
    authService,
    config,
    courseFactory,
    googleAnalyticsService,
    me,
    page,
    curatedCohortFactory,
    studentFactory,
    studentSearchService,
    utilService,
    validationService,
    visualizationService,
    $location,
    $q,
    $rootScope,
    $scope,
    $stateParams
  ) {

    page.loading(true);

    $scope.student = {
      enrollmentTerms: null
    };
    $scope.currentEnrollmentTermId = config.currentEnrollmentTermId;
    $scope.currentEnrollmentTerm = config.currentEnrollmentTerm;
    $scope.demoMode = config.demoMode;
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.lastActivityInContext = utilService.lastActivityInContext;
    $scope.isAscUser = authService.isAscUser();
    $scope.isCoeUser = authService.isCoeUser();
    $scope.myCuratedCohorts = _.clone(me.myCuratedCohorts);
    $scope.parseInt = parseInt;
    $scope.showAllTerms = false;
    $scope.showDismissedAlerts = false;

    $scope.dismissAlert = function(alertId) {
      studentFactory.dismissAlert(alertId).then(function() {
        var dismissed = _.remove($scope.alerts.shown, {id: alertId});
        Array.prototype.push.apply($scope.alerts.dismissed, dismissed);
      }).catch(function(error) {
        if (error) {
          $scope.error = validationService.parseError(err);
        } else {
          throw error;
        }
      });
    };

    var getPreferredName = function() {
      return _.get($scope.student, 'sisProfile.preferredName') || _.get($scope.student, 'canvasUserName');
    };

    var identifyCuratedCohortsWithStudent = function() {
      _.each($scope.myCuratedCohorts, function(cohort) {
        _.each(cohort.students, function(student) {
          cohort.selected = $scope.student.sid === student.sid;
          if (cohort.selected) {
            // Break from loop
            return false;
          }
        });
      });
    };

    var loadStudent = function(uid) {
      page.loading(true);
      var preferredName = null;
      studentFactory.analyticsPerUser(uid).then(function(analytics) {
        var student = analytics.data;
        var sid = student.sid;
        if (!sid) {
          return $q.reject({
            status: 404,
            message: 'No student found with UID ' + uid
          });
        }
        $scope.student = student;
        identifyCuratedCohortsWithStudent();
        preferredName = getPreferredName();

        _.each($scope.student.enrollmentTerms, function(term) {
          // Merge in unmatched canvas sites
          var unmatched = _.map(term.unmatchedCanvasSites, function(c) {
            // course_code is often valuable (eg, 'ECON 1 - LEC 001'), occasionally not (eg, CCN). Use it per strict criteria:
            var useCourseCode = (/^[A-Z].*[A-Za-z]{3} \d/).test(c.courseCode);
            return _.merge(c, {
              displayName: useCourseCode ? c.courseCode : c.courseName,
              title: useCourseCode ? c.courseName : null,
              canvasSites: [ c ]
            });
          });
          term.enrollments = _.concat(term.enrollments, unmatched);
          _.each(term.enrollments, function(course) {
            _.each(course.sections, function(section) {
              course.waitlisted = course.waitlisted || section.enrollmentStatus === 'W';
              section.displayName = section.component + ' ' + section.sectionNumber;
              section.isViewableOnCoursePage = section.primary;
            });
          });
        });

      }).then(function() {
        studentFactory.getAlerts($scope.student.sid).then(function(alerts) {
          $scope.alerts = alerts.data;
        });
        visualizationService.showUnitsChart($scope.student);
        if (!config.demoMode) {
          $rootScope.pageTitle = _.get($scope.student, 'name') || preferredName;
        }

      }).then(function() {
        page.loading(false);
        googleAnalyticsService.track('student', 'view-profile', preferredName, parseInt(uid, 10));

      }).catch(function(err) {
        $scope.error = validationService.parseError(err);
        page.loading(false);

      });
    };

    $scope.curatedCohortCheckboxClick = function(cohort) {
      if (cohort.selected) {
        curatedCohortFactory.addStudent(cohort, $scope.student).then(angular.noop);
      } else {
        curatedCohortFactory.removeStudent(cohort, $scope.student).then(angular.noop);
      }
    };

    $rootScope.$on('curatedCohortCreated', function(event, data) {
      $scope.myCuratedCohorts.push(data.cohort);
    });

    var init = function() {
      var uid = $stateParams.uid;
      loadStudent(uid);
    };

    init();
  });

}(window.angular));
