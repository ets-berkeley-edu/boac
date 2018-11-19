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
    status,
    utilService,
    validationService,
    visualizationService
  ) {

    $scope.inDemoMode = status.inDemoMode;
    $scope.isAscUser = authService.isAscUser();
    page.loading(true);
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.pagination = {
      currentPage: 1,
      defaultItemsPerPage: 50,
      itemsPerPage: 50,
      selected: {
        itemsPerPage: 50
      },
      options: [{label: 'Show 50', value: 50}, {label: 'Show 100', value: 100}]
    };
    $scope.tab = 'list';

    $scope.getDisplayProperty = visualizationService.getDisplayProperty;
    $scope.hasPlottableProperty = visualizationService.hasPlottableProperty;

    $scope.axisLabels = {};
    var metrics = ['analytics.currentScore', 'analytics.lastActivity', 'cumulativeGPA'];
    var lastTermId = utilService.previousSisTermId(config.currentEnrollmentTermId);
    var previousTermId = utilService.previousSisTermId(lastTermId);
    metrics.push('termGpa.' + previousTermId);
    metrics.push('termGpa.' + lastTermId);
    _.each(metrics, function(metric) {
      $scope.axisLabels[metric] = visualizationService.formatForDisplay(metric);
    });

    $scope.selectedAxes = {
      x: 'analytics.currentScore',
      y: 'cumulativeGPA'
    };

    $scope.exceedsMatrixThresholdMessage = utilService.exceedsMatrixThresholdMessage;

    $scope.$watch('pagination.currentPage', function() {
      if (!page.isLoading()) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    var featureSearchedStudent = function(data) {
      var section = _.clone(data);
      var subject = _.remove(section.students, function(student) {
        return student.uid === _.get($location.search(), 'u');
      });
      section.students = _.union(subject, section.students);
      return section;
    };

    var updateCourseData = function(response) {
      $rootScope.pageTitle = response.data.displayName;
      $scope.section = featureSearchedStudent(response.data);
      if (utilService.exceedsMatrixThreshold(_.get($scope.section, 'totalStudentCount'))) {
        $scope.matrixDisabledMessage = utilService.exceedsMatrixThresholdMessage;
      } else {
        var plottableStudents = visualizationService.partitionPlottableStudents(
          $scope.selectedAxes.x,
          $scope.selectedAxes.y,
          $scope.section.students
        );
        if (plottableStudents[0].length === 0) {
          $scope.matrixDisabledMessage = 'No student data is available to display.';
        } else {
          $scope.matrixDisabledMessage = null;
        }
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

    var refreshScatterplot = $scope.refreshScatterplot = function() {
      var goToUserPage = function(uid) {
        $location.state($location.absUrl());
        $location.path('/student/' + uid);
        // The intervening visualizationService code moves out of Angular and into d3, hence the extra kick of $apply.
        $scope.$apply();
      };
      visualizationService.scatterplotRefresh(
        $scope.section.students,
        $scope.section.meanMetrics,
        $scope.selectedAxes,
        goToUserPage,
        function(studentsWithoutData, zoom) {
          // List of students-without-data is rendered below the scatterplot.
          $scope.studentsWithoutData = studentsWithoutData;
          // Make d3 zoom available to the scope.
          $scope.zoom = zoom;
          $scope.zoomIn = function() {
            zoom.programmaticZoom(2, function() { $scope.$apply(); });
          };
          $scope.zoomOut = function() {
            zoom.programmaticZoom(0.5, function() { $scope.$apply(); });
          };
        }
      );
    };

    var onTab = $scope.onTab = function(tabName) {
      page.loading(true);
      $scope.tab = tabName;
      $location.search('tab', $scope.tab);
      if (tabName === 'matrix') {
        var sectionId = $stateParams.sectionId;
        return courseFactory.getSection($stateParams.termId, sectionId).then(function(response) {
          updateCourseData(response);
          refreshScatterplot();
          page.loading(false);
          if ($scope.section) {
            var label = _.get($scope.section, 'termName') + ' ' + _.get($scope.section, 'displayName');
            googleAnalyticsService.track('Course', 'matrix', label, sectionId);
          }
        });
      } else if (tabName === 'list') {
        if ($scope.pagination.currentPage > 1 && $scope.section && $scope.section.students.length > $scope.pagination.itemsPerPage) {
          var start = ($scope.pagination.currentPage - 1) * $scope.pagination.itemsPerPage;
          $scope.section.students = _.slice($scope.section.students, start, start + $scope.pagination.itemsPerPage);
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

    $scope.resizePage = function(selectedItemsPerPage) {
      var currentItemsPerPage = $scope.pagination.itemsPerPage;
      $scope.pagination.currentPage = Math.round($scope.pagination.currentPage * (currentItemsPerPage / selectedItemsPerPage));
      $scope.pagination.itemsPerPage = selectedItemsPerPage;
      $location.search('p', $scope.pagination.currentPage);
      $location.search('s', $scope.pagination.itemsPerPage);

      refreshListView().catch(function(err) {
        $scope.error = validationService.parseError(err);
        page.loading(false);
      });
    };

    var initPagination = function(args) {
      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
      }
      if (args.s && !isNaN(args.s)) {
        var itemsPerPage = parseInt(args.s, 10);
        if (_.includes(_.map($scope.pagination.options, 'value'), itemsPerPage)) {
          $scope.pagination.itemsPerPage = itemsPerPage;
          $scope.pagination.selected.itemsPerPage = itemsPerPage;
        } else {
          $location.search('s', $scope.pagination.itemsPerPage);
        }
      }
    };

    var initViewMode = function(args) {
      $scope.tab = _.includes(['list', 'matrix'], args.tab) ? args.tab : $scope.tab;
    };

    var init = function() {
      var args = _.clone($location.search());
      initViewMode(args);
      initPagination(args);

      onTab($scope.tab)
        .catch(function(err) {
          $scope.error = validationService.parseError(err);
          page.loading(false);
        }).then(function() {
          if ($scope.section) {
            var label = _.get($scope.section, 'termName') + ' ' + _.get($scope.section, 'displayName');
            googleAnalyticsService.track('Course', 'view', label, $stateParams.sectionId);
          }
        });
    };

    init();
  });

}(window.angular));
