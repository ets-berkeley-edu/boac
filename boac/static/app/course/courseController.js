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
    cohortService,
    courseFactory,
    googleAnalyticsService,
    utilService,
    watchlistFactory,
    $anchorScroll,
    $base64,
    $location,
    $scope,
    $state,
    $stateParams,
    $timeout) {

    $scope.isLoading = true;

    $scope.studentProfile = utilService.studentProfile;

    $scope.tab = 'list';

    /**
     * Draw scatterplot graph.
     *
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
        var absUrl = $location.absUrl();
        $location.state(absUrl);
        var encodedAbsUrl = encodeURIComponent($base64.encode(absUrl));
        $state.go('user', {uid: uid, r: encodedAbsUrl});
      });
      // List of students-without-data is rendered below the scatterplot.
      $scope.studentsWithoutData = partitions[1];
      return callback();
    };

    $scope.onTab = function(tabName) {
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

    var init = function() {
      var args = _.clone($location.search());

      courseFactory.getSection($stateParams.termId, $stateParams.sectionId).then(function(response) {
        $scope.section = response.data;

      }).catch(function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;

      }).then(function() {
        watchlistFactory.getMyWatchlist().then(function(response) {
          $scope.myWatchlist = response.data;
          // Begin with matrix view if arg is present
          if (args.v && _.includes(['list', 'matrix'], args.v)) {
            $scope.tab = args.v;
            $scope.onTab($scope.tab);
          } else {
            $scope.isLoading = false;
          }
          if (args.a) {
            $timeout(function() {
              // Scroll to anchor if returning from student profile page
              $scope.anchor = args.a;
              $location.search('a', null).replace();
              $anchorScroll.yOffset = 50;
              $anchorScroll(args.a);
            });
          }
          googleAnalyticsService.track(
            'course',
            'view',
            $scope.section.termName + ' ' + $scope.section.displayName + ' ' + $scope.section.sectionNum
          );
        });
      });
    };

    init();
  });

}(window.angular));
