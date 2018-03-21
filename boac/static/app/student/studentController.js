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
    studentFactory,
    studentService,
    utilService,
    watchlistFactory,
    $location,
    $rootScope,
    $scope,
    $stateParams
  ) {

    $scope.demoMode = config.demoMode;

    $scope.student = {
      canvasProfile: null,
      enrollmentTerms: null,
      isLoading: true
    };

    $scope.showAllTerms = false;
    $scope.showDismissedAlerts = false;

    $scope.dismissAlert = function(alertId) {
      studentFactory.dismissAlert(alertId).then(function() {
        var dismissed = _.remove($scope.alerts.shown, {id: alertId});
        Array.prototype.push.apply($scope.alerts.dismissed, dismissed);
      }).catch(function(error) {
        if (error) {
          $scope.error = utilService.parseError(err);
        } else {
          throw error;
        }
      });
    };

    var getPreferredName = function() {
      return _.get($scope.student, 'sisProfile.preferredName') || _.get($scope.student, 'canvasProfile.name');
    };

    $scope.goToCourse = function(event, termId, sectionId) {
      event.stopPropagation();
      var name = config.demoMode ? null : getPreferredName();
      utilService.goTo('/course/' + termId + '/' + sectionId, name);
    };

    var loadStudent = function(uid, callback) {
      $scope.student.isLoading = true;
      var preferredName = null;
      studentFactory.analyticsPerUser(uid).then(function(analytics) {
        $scope.student = analytics.data;
        preferredName = getPreferredName();

        courseFactory.getCachedCourseSections().then(function(response) {
          var cachedSections = response.data;

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
            utilService.decorateEnrollments(term.enrollments, cachedSections[term.termId]);
          });
        });

      }).catch(function(err) {
        $scope.error = utilService.parseError(err);

      }).then(function() {
        var athleticsProfile = $scope.student.athleticsProfile;
        if (athleticsProfile) {
          athleticsProfile.fullName = athleticsProfile.firstName + ' ' + athleticsProfile.lastName;
          if (athleticsProfile.sid) {
            studentFactory.getAlerts(athleticsProfile.sid).then(function(alerts) {
              $scope.alerts = alerts.data;
            });
            studentService.showUnitsChart($scope.student);
          }
        }
        if (!config.demoMode) {
          $rootScope.pageTitle = _.get(athleticsProfile, 'fullName') || preferredName;
        }

      }).then(function() {
        $scope.student.isLoading = false;
        googleAnalyticsService.track('student', 'view-profile', preferredName, parseInt(uid, 10));

      }).then(callback);
    };

    var init = function() {
      var args = _.clone($location.search());
      var uid = $stateParams.uid;

      loadStudent(uid, function() {
        if (args.a) {
          // We are returning to this student after a detour on course/section page...
          $scope.anchor = args.a;
          utilService.anchorScroll($scope.anchor);
        } else {
          // ...or, maybe we are fresh arrival from cohort page.
          $scope.returnUrl = utilService.unpackReturnUrl(uid);
          $scope.returnLabel = utilService.constructReturnToLabel($scope.returnUrl);
          $scope.hideFeedbackLink = !!$scope.returnUrl;
        }
        $scope.isWatchlistLoading = true;
        watchlistFactory.getMyWatchlist().then(function(response) {
          $scope.myWatchlist = response.data;
          $scope.isWatchlistLoading = false;
        });
      });
    };

    init();
  });

}(window.angular));
