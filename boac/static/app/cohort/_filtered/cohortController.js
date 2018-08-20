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

  angular.module('boac').controller('_FilteredCohortController', function(
    $anchorScroll,
    $location,
    $rootScope,
    $scope,
    $state,
    cohortService,
    filterCriteriaFactory,
    filterCriteriaService,
    filteredCohortFactory,
    page,
    studentFactory,
    studentSearchService,
    utilService,
    validationService,
    visualizationService
  ) {

    var queryArgs = _.clone($location.search());

    /**
     * Cohort metadata ONLY. Search results (ie, students) are kept in $scope.search. Properties are null if user is
     * viewing unsaved search results.
     */
    $scope.cohort = {
      id: null,
      name: null,
      isOwnedByCurrentUser: null,
      isReadOnly: null
    };
    $scope.exceedsMatrixThresholdMessage = utilService.exceedsMatrixThresholdMessage;
    $scope.orderBy = studentSearchService.getSortByOptionsForSearch();
    $scope.hasFilterCriteria = false;
    $scope.renameMode = {
      error: null,
      input: null,
      on: false
    };
    $scope.tab = queryArgs.tab || 'list';

    /**
     * Object (ie, model) rendered on page.
     */
    $scope.search = {
      orderBy: studentSearchService.getSortByOptionsForSearch(),
      pagination: studentSearchService.initPagination(),
      results: {
        students: null,
        totalStudentCount: null
      }
    };

    $scope.filterCriteriaComponent = {
      filters: {
        added: null
      }
    };

    $rootScope.$on('filteredCohortDeleted', function(event, data) {
      if (data.cohort.id === $scope.cohort.id) {
        $state.go('home');
      }
    });

    var errorHandler = function(error) {
      if (error.status === 404) {
        $location.replace().path('/404');
      } else {
        $scope.error = validationService.parseError(error);
        page.loading(false);
        return $scope.error;
      }
    };

    $scope.enterRenameMode = function(originalName) {
      $scope.renameMode.input = originalName;
      $scope.renameMode.on = true;
    };

    var exitRenameMode = $scope.exitRenameMode = function() {
      $scope.renameMode.on = false;
      $scope.renameMode.input = null;
    };

    $scope.rename = function() {
      validationService.validateName({id: $scope.cohort.id, name: $scope.renameMode.input}, function(error) {
        if (error) {
          $scope.renameMode.error = errorHandler(error);
        } else {
          filteredCohortFactory.rename($scope.cohort.id, $scope.renameMode.input).then(function() {
            $scope.cohort.name = $scope.renameMode.input;
            exitRenameMode();
          }).catch(errorHandler);
        }
      });
    };

    var scatterplotRefresh = function() {
      if ($scope.tab === 'matrix') {
        var goToUserPage = function(uid) {
          $location.state($location.absUrl());
          $location.path('/student/' + uid);
          // The intervening visualizationService code moves out of Angular and into d3 thus the extra kick of $apply.
          $scope.$apply();
        };
        visualizationService.scatterplotRefresh($scope.search.results.students, goToUserPage, function(yAxisMeasure, studentsWithoutData) {
          $scope.yAxisMeasure = yAxisMeasure;
          // List of students-without-data is rendered below the scatterplot.
          $scope.studentsWithoutData = studentsWithoutData;
        });
      }
    };

    var loadSavedCohort = function(cohortId, orderBy, offset, limit, callback) {
      filteredCohortFactory.getCohort(cohortId, orderBy, offset, limit).then(function(response) {
        var cohort = response.data;

        // Reset browser location
        $rootScope.pageTitle = cohort.name;
        $location.url($location.path());
        $location.search('c', cohort.id);
        $location.search('tab', $scope.tab);

        _.extend($scope.search, {
          filterCriteria: cohort.filterCriteria,
          results: {
            students: cohort.students,
            totalStudentCount: cohort.totalStudentCount
          }
        });
        // Grab a limited set of properties
        var metadataKeys = _.keys($scope.cohort);
        $scope.cohort = _.pick(cohort, metadataKeys);

      }).then(scatterplotRefresh).then(callback).catch(errorHandler);
    };

    var search = function(filterCriteria, orderBy, offset, limit, callback) {
      filterCriteriaService.updateLocation(filterCriteria, $scope.search.pagination.currentPage);
      studentFactory.getStudents(filterCriteria, orderBy, offset, limit).then(function(response) {
        $scope.cohort.name = queryArgs.cohortName;
        $scope.cohort.name = $scope.cohort.name || cohortService.getSearchPageTitle(filterCriteria);
        $rootScope.pageTitle = $scope.cohort.name || 'Filtered Cohort';
        _.extend($scope.search, {
          filterCriteria: filterCriteria,
          results: {
            students: response.data.students,
            totalStudentCount: response.data.totalStudentCount
          }
        });

      }).then(scatterplotRefresh).then(callback).catch(errorHandler);
    };

    var showDetails = $scope.showDetails = function(show, defaultValue) {
      var detailsShowing = show === null ? defaultValue : utilService.toBoolOrNull(show);
      $location.search('details', _.toLower(detailsShowing));
      $scope.detailsShowing = detailsShowing;
    };

    var init = $scope.nextPage = $scope.onTab = function(tab, searchCriteria, offsetOverride, limitOverride) {
      var cohortId = filterCriteriaService.getCohortIdFromLocation();
      var criteria = searchCriteria || filterCriteriaService.getFilterCriteriaFromLocation() || null;
      var hasFilterCriteria = $scope.hasFilterCriteria = !!cohortId || !!_.find(_.values(criteria));
      var limit = limitOverride || $scope.search.pagination.itemsPerPage;
      var offset = offsetOverride === null ? ($scope.search.pagination.currentPage - 1) * limit : offsetOverride;
      var sortOrder = filterCriteriaFactory.getPrimaryFilterSortOrder();
      var done = function() {
        $scope.studentCountExceedsMatrixThreshold = utilService.exceedsMatrixThreshold(_.get($scope, 'search.results.totalStudentCount'));
        page.loading(false);
      };

      page.loading(true);
      $anchorScroll();

      filterCriteriaService.getAvailableFilters(filterCriteriaFactory.getFilterDefinitions(), function(availableFilters) {
        // Matrix view requires cohort/search criteria
        $scope.tab = hasFilterCriteria ? tab || $scope.tab : 'list';
        $location.search('tab', $scope.tab);
        if ($scope.tab === 'matrix') {
          if (cohortId > 0) {
            loadSavedCohort(cohortId, null, 0, Number.MAX_SAFE_INTEGER, done);
          } else {
            search(criteria, null, 0, Number.MAX_SAFE_INTEGER, done);
          }

        } else {
          $scope.availableFilters = _.reject(_.map(sortOrder, function(key) {
            // Return null to insert divider in dropdown menu.
            return key && _.find(availableFilters, ['key', key]);
          }), _.isUndefined);

          if (cohortId > 0) {
            loadSavedCohort(cohortId, $scope.search.orderBy.selected, offset, limit, done);
            showDetails(queryArgs.details, false);

          } else if (hasFilterCriteria) {
            search(criteria, $scope.search.orderBy.selected, offset, limit, done);
            showDetails(queryArgs.details, true);

          } else {
            // No query args is create-cohort mode
            showDetails(true);
            $rootScope.pageTitle = 'Create a Filtered Cohort';
            done();
          }
        }
      });
    };

    $scope.executeSearchFunction = function(searchCriteria) {
      init('list', searchCriteria);
    };

    init();

  });
}(window.angular));
