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
    boxplotService,
    config,
    googleAnalyticsService,
    studentFactory,
    watchlistFactory,
    $base64,
    $location,
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
        if (error.data) {
          $scope.error = _.truncate(error.data.message, {length: 200}) || 'An unexpected server error occurred.';
        } else {
          throw error;
        }
      });
    };

    var loadStudent = function(uid) {
      $scope.student.isLoading = true;
      studentFactory.analyticsPerUser(uid).then(function(analytics) {
        $scope.student = analytics.data;
        // Track view event
        var preferredName = $scope.student.sisProfile && $scope.student.sisProfile.preferredName;
        googleAnalyticsService.track('student', 'view-profile', preferredName, parseInt(uid, 10));
      }).catch(function(error) {
        $scope.error = _.truncate(error.data.message, {length: 200}) || 'An unexpected server error occurred.';
      }).then(function() {
        var athleticsProfile = $scope.student.athleticsProfile;
        if (athleticsProfile) {
          athleticsProfile.fullName = athleticsProfile.firstName + ' ' + athleticsProfile.lastName;
          if (athleticsProfile.sid) {
            studentFactory.getAlerts(athleticsProfile.sid).then(function(alerts) {
              $scope.alerts = alerts.data;
            });
          }
        }
        $scope.student.isLoading = false;
      });
    };

    var prepareReturnUrl = function(uid) {
      var encodedReturnUrl = $location.search().r;
      if (!_.isEmpty(encodedReturnUrl)) {
        $location.search('r', null).replace();
        var url = $base64.decode(decodeURIComponent(encodedReturnUrl));
        var separator = _.includes(url, '?') ? '&' : '?';
        $scope.returnUrl = url + separator + 'a=' + uid;
        $scope.hideFeedbackLink = true;
      }
    };

    var init = function() {
      var uid = $stateParams.uid;
      loadStudent(uid);
      prepareReturnUrl(uid);
      $scope.isWatchlistLoading = true;
      watchlistFactory.getMyWatchlist().then(function(response) {
        $scope.myWatchlist = response.data;
        $scope.isWatchlistLoading = false;
      });
    };

    $scope.drawBoxplot = function(termId, displayName, courseId, metric) {
      var term = _.find($scope.student.enrollmentTerms, {termId: termId});

      var courseSites;
      if (displayName === 'unmatchedCanvasSites') {
        courseSites = term.unmatchedCanvasSites;
      } else {
        var enrollment = _.find(term.enrollments, {displayName: displayName});
        courseSites = enrollment.canvasSites;
      }

      var course = _.find(courseSites, {canvasCourseId: courseId});
      var elementId = 'boxplot-' + courseId + '-' + metric;
      boxplotService.drawBoxplotStudent(elementId, course.analytics[metric]);
    };

    init();
  });

}(window.angular));
