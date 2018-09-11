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
    $location,
    $rootScope,
    $scope,
    $stateParams,
    authService,
    config,
    courseFactory,
    googleAnalyticsService,
    page,
    utilService,
    validationService,
    visualizationService
  ) {

    $scope.demoMode = config.demoMode;
    $scope.isAscUser = authService.isAscUser();
    page.loading(true);
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.pagination = {
      currentPage: 1,
      itemsPerPage: 50
    };
    $scope.tab = 'list';

    $scope.exceedsMatrixThresholdMessage = utilService.exceedsMatrixThresholdMessage;

    $scope.$watch('pagination.currentPage', function() {
      if (!page.isLoading()) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    var updateCourseData = function(response) {
      $rootScope.pageTitle = response.data.displayName;
      $scope.section = response.data;
      if (utilService.exceedsMatrixThreshold(_.get($scope.section, 'totalStudentCount'))) {
        $scope.matrixDisabledMessage = utilService.exceedsMatrixThresholdMessage;
      } else if (visualizationService.partitionPlottableStudents($scope.section.students)[0].length === 0) {
        $scope.matrixDisabledMessage = 'No student data is available to display.';
      } else {
        $scope.matrixDisabledMessage = null;
      }
    };

    var refreshListView = function() {
      var limit = $scope.pagination.itemsPerPage;
      var offset = $scope.pagination.currentPage === 0 ? 0 : ($scope.pagination.currentPage - 1) * limit;
      return courseFactory.getSection($stateParams.termId, $stateParams.sectionId, offset, limit).then(function(response) {
        updateCourseData(response);
        page.loading(false);
      });
    };

    var onTab = $scope.onTab = function(tabName) {
      page.loading(true);
      $scope.tab = tabName;
      $location.search('tab', $scope.tab);
      if (tabName === 'matrix') {
        var goToUserPage = function(uid) {
          $location.state($location.absUrl());
          $location.path('/student/' + uid);
          // The intervening visualizationService code moves out of Angular and into d3 thus the extra kick of $apply.
          $scope.$apply();
        };
        return courseFactory.getSection($stateParams.termId, $stateParams.sectionId).then(function(response) {
          updateCourseData(response);
          visualizationService.scatterplotRefresh($scope.section.students, goToUserPage, function(yAxisMeasure, studentsWithoutData) {
            $scope.yAxisMeasure = yAxisMeasure;
            // List of students-without-data is rendered below the scatterplot.
            $scope.studentsWithoutData = studentsWithoutData;
          });
          page.loading(false);
        });
      } else if (tabName === 'list') {
        if ($scope.pagination.currentPage > 1 && $scope.section && $scope.section.students.length > 50) {
          var start = ($scope.pagination.currentPage - 1) * 50;
          $scope.section.students = _.slice($scope.section.students, start, start + 50);
        }
        return refreshListView();
      }
    };

    $scope.nextPage = function() {
      refreshListView().catch(function(err) {
        $scope.error = validationService.parseError(err);
        page.loading(false);
      });
    };

    var init = function() {
      var args = _.clone($location.search());
      // Begin with matrix view if arg is present
      $scope.tab = _.includes(['list', 'matrix'], args.tab) ? args.tab : $scope.tab;

      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
      }
      onTab($scope.tab)
        .catch(function(err) {
          $scope.error = validationService.parseError(err);
          page.loading(false);
        }).then(function() {
          googleAnalyticsService.track(
            'course',
            'view',
            $scope.section.termName + ' ' + $scope.section.displayName + ' ' + $scope.section.sectionNum
          );
        });
    };

    init();
  });

}(window.angular));
