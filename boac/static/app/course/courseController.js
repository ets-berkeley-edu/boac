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

  angular.module('boac').controller('CourseController', function(
    boxplotService,
    cohortService,
    courseFactory,
    googleAnalyticsService,
    utilService,
    watchlistFactory,
    $base64,
    $location,
    $rootScope,
    $scope,
    $state,
    $stateParams
  ) {

    $scope.isLoading = true;
    $scope.tab = 'list';

    var goToStudent = $scope.goToStudent = function(uid) {
      utilService.goTo('/student/' + uid, $scope.section.displayName);
    };

    /**
     * @param  {Function}      callback       Standard callback
     * @return {void}
     */
    var scatterplotRefresh = function(callback) {
      // Plot the cohort
      var yAxisMeasure = $scope.yAxisMeasure = $location.search().yAxis || 'analytics.courseCurrentScore';
      var partitions = _.partition($scope.section.students, function(student) {
        return _.isFinite(_.get(student, 'analytics.pageViews.percentile')) &&
          _.isFinite(_.get(student, yAxisMeasure + '.percentile'));
      });
      // Pass along a subset of students that have useful data.
      cohortService.drawScatterplot(partitions[0], yAxisMeasure, function(uid) {
        $location.state($location.absUrl());
        goToStudent(uid);
      });
      // List of students-without-data is rendered below the scatterplot.
      $scope.studentsWithoutData = partitions[1];
      return callback();
    };

    var onTab = $scope.onTab = function(tabName) {
      $scope.isLoading = true;
      $scope.tab = tabName;
      $location.search('v', $scope.tab);
      if (tabName === 'matrix') {
        scatterplotRefresh(function() {
          $scope.isLoading = false;
        });
      } else if (tabName === 'list') {
        $scope.isLoading = false;
      }
    };

    $scope.drawBoxplot = function(canvasSite, uid, metricId) {
      var elementId = 'boxplot-' + uid + '-' + metricId;
      boxplotService.drawBoxplotStudent(elementId, canvasSite.analytics[metricId]);
    };

    var init = function() {
      // Maybe we are arriving from student page.
      $scope.returnUrl = utilService.unpackReturnUrl();
      $scope.returnLabel = utilService.constructReturnToLabel($scope.returnUrl);
      $scope.hideFeedbackLink = !!$scope.returnUrl;

      var args = _.clone($location.search());

      courseFactory.getSection($stateParams.termId, $stateParams.sectionId).then(function(response) {
        $scope.section = response.data;
        $rootScope.pageTitle = $scope.section.displayName;
        var students = $scope.section.students;
        // Draw boxplots when Angular is done rendering elements within repeaters
        $scope.$$postDigest(boxplotService.drawBoxplots(students));
        // Cherry-pick section enrollment
        _.each(students, function(student) {
          _.each(student.term.enrollments, function(e) {
            if (e.displayName === $scope.section.displayName) {
              student.enrollment = e;
            }
          });
        });
      }).catch(function(err) {
        $scope.error = utilService.parseError(err);

      }).then(function() {
        watchlistFactory.getMyWatchlist().then(function(response) {
          $scope.myWatchlist = response.data;
          // Begin with matrix view if arg is present
          if (args.v && _.includes(['list', 'matrix'], args.v)) {
            $scope.tab = args.v;
            onTab($scope.tab);
          }
          googleAnalyticsService.track(
            'course',
            'view',
            $scope.section.termName + ' ' + $scope.section.displayName + ' ' + $scope.section.sectionNum
          );
        });
      }).then(function() {
        $scope.isLoading = false;
        if (args.a) {
          // Scroll to anchor
          $scope.anchor = args.a;
          utilService.anchorScroll($scope.anchor);
        }
      });
    };

    init();
  });

}(window.angular));
