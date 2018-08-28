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

  angular.module('boac').controller('FilteredCohortController', function(
    $anchorScroll,
    $location,
    $rootScope,
    $scope,
    $state,
    cohortService,
    cohortUtils,
    config,
    filteredCohortFactory,
    page,
    studentFactory,
    utilService,
    validationService,
    visualizationService
  ) {

    /**
     * Cohort metadata ONLY. Search results (ie, students) are kept in $scope.search. Properties are null if user is
     * viewing unsaved search results.
     */
    $scope.cohort = {
      id: null,
      name: null,
      isOwnedByCurrentUser: null
    };
    $scope.demoMode = config.demoMode;
    $scope.exceedsMatrixThresholdMessage = utilService.exceedsMatrixThresholdMessage;
    $scope.hasFilterCriteria = false;
    $scope.renameMode = {
      error: null,
      input: null,
      on: false
    };
    $scope.tab = $location.search().tab || 'list';

    /**
     * Object (ie, model) rendered on page.
     */
    $scope.search = {
      orderBy: cohortService.getSortByOptionsForSearch(),
      pagination: cohortService.initPagination(),
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

    $scope.rename = function($event) {
      $event.stopPropagation();
      var cohortName = $scope.renameMode.input;
      validationService.validateName({id: $scope.cohort.id, name: cohortName}, function(error) {
        if (error) {
          $scope.renameMode.error = errorHandler(error);
        } else {
          filteredCohortFactory.rename($scope.cohort.id, cohortName).then(function() {
            $scope.cohort.name = cohortName;
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

    var registerCohortMetadata = function(cohort) {
      $rootScope.pageTitle = cohort.name;
      // Reset browser location
      $location.url($location.path());
      $location.search('c', cohort.id);
      $location.search('details', $scope.filtersVisible);
      $location.search('orderBy', $scope.search.orderBy.selected);
      $location.search('tab', $scope.tab);
      // Grab a limited set of properties
      var metadataKeys = _.keys($scope.cohort);
      $scope.cohort = _.pick(cohort, metadataKeys);
    };

    var loadSavedCohort = function(cohortId, orderBy, offset, limit, callback) {
      filteredCohortFactory.getCohort(cohortId, orderBy, offset, limit).then(function(response) {
        var cohort = response.data;

        registerCohortMetadata(cohort);
        _.extend($scope.search, {
          filterCriteria: cohort.filterCriteria,
          results: {
            students: cohort.students,
            totalStudentCount: cohort.totalStudentCount
          }
        });

      }).then(scatterplotRefresh).then(callback).catch(errorHandler);
    };

    var updateLocation = function(definitions, filterCriteria, currentPage) {
      $location.search('page', currentPage);

      _.each(filterCriteria, function(value, key) {
        var definition = _.find(definitions, ['key', key]);
        if (definition && _.size(typeof value === 'boolean' ? _.toString(value) : value)) {
          $location.search(definition.param, value);
        }
      });
    };

    var executeSearch = function(filterCriteria, orderBy, offset, limit, callback) {
      updateLocation($scope.filterDefinitions, filterCriteria, $scope.search.pagination.currentPage);
      studentFactory.getStudents(filterCriteria, orderBy, offset, limit).then(function(response) {
        $scope.cohort.name = $location.search().cohortName;
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

    var makeFiltersVisible = $scope.makeFiltersVisible = function(show, defaultValue) {
      var filtersVisible = _.isNil(show) ? defaultValue : utilService.toBoolOrNull(show);
      $location.search('details', _.toLower(filtersVisible));
      $scope.filtersVisible = filtersVisible;
    };

    var getFilterCriteriaFromLocation = function(definitions) {
      var queryArgs = _.clone($location.search());
      var filterCriteria = {};

      _.each(definitions, function(d) {
        filterCriteria[d.key] = cohortUtils.translateQueryArg(d, queryArgs[d.param]);
      });
      return filterCriteria;
    };

    var init = $scope.nextPage = $scope.onTab = function(tab, searchCriteria, offsetOverride, limitOverride) {
      var cohortId = parseInt($location.search().c, 10);
      var limit = limitOverride || $scope.search.pagination.itemsPerPage;
      var offset = _.isNil(offsetOverride) ? ($scope.search.pagination.currentPage - 1) * limit : offsetOverride;
      offset = offset < 0 ? 0 : offset;
      var queryArgs = _.clone($location.search());
      var done = function() {
        $scope.studentCountExceedsMatrixThreshold = utilService.exceedsMatrixThreshold(_.get($scope, 'search.results.totalStudentCount'));
        page.loading(false);
      };

      page.loading(true);
      $anchorScroll();

      filteredCohortFactory.getFilterDefinitions().then(function(response) {
        var definitions = $scope.filterDefinitions = response.data;
        var criteria = searchCriteria || getFilterCriteriaFromLocation(definitions) || null;
        var hasFilterCriteria = $scope.hasFilterCriteria = !!cohortId || !!_.find(_.values(criteria));

        $scope.tab = hasFilterCriteria ? tab || $scope.tab : 'list';
        $location.search('tab', $scope.tab);

        if (queryArgs.orderBy && _.find($scope.search.orderBy.options, ['value', queryArgs.orderBy])) {
          $scope.search.orderBy.selected = queryArgs.orderBy;
        }
        if ($scope.tab === 'matrix') {
          if (cohortId > 0) {
            loadSavedCohort(cohortId, null, 0, Number.MAX_SAFE_INTEGER, done);
          } else {
            executeSearch(criteria, null, 0, Number.MAX_SAFE_INTEGER, done);
          }

        } else if (cohortId > 0) {
          loadSavedCohort(cohortId, $scope.search.orderBy.selected, offset, limit, done);
          makeFiltersVisible(queryArgs.details, false);

        } else if (hasFilterCriteria) {
          executeSearch(criteria, $scope.search.orderBy.selected, offset, limit, done);
          makeFiltersVisible(queryArgs.details, true);

        } else {
          // No query args is create-cohort mode
          makeFiltersVisible(true);
          $rootScope.pageTitle = 'Create a Filtered Cohort';
          done();
        }
      });
    };

    $scope.$watch('search.orderBy.selected', function(value) {
      if (value && !page.isLoading()) {
        $location.search('orderBy', $scope.search.orderBy.selected);
        $scope.search.pagination.currentPage = 1;
        init();
      }
    });

    $scope.callbacks = {
      executeSearch: function(searchCriteria) {
        $scope.search.pagination.currentPage = 1;
        $scope.cohort = {id: null, name: null, isOwnedByCurrentUser: null};
        registerCohortMetadata($scope.cohort);
        init('list', searchCriteria);
      },
      onSave: function(cohort) {
        // Grab metadata without reloading page
        registerCohortMetadata(cohort);
      }
    };

    init();

  });
}(window.angular));
