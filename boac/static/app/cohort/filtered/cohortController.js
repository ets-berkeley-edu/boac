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
    authService,
    cohortService,
    cohortUtils,
    filteredCohortFactory,
    page,
    status,
    studentFactory,
    utilService,
    validationService
  ) {

    /**
     * Cohort metadata ONLY. Search results (ie, students) are kept in $scope.search. Properties are null if user is
     * viewing unsaved search results.
     */
    $scope.inDemoMode = status.inDemoMode;
    $scope.isAscUser = authService.isAscUser();
    $scope.isSearching = false;
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.renameMode = {
      error: null,
      input: null,
      on: false
    };

    /**
     * Object (ie, model) rendered on page.
     */
    var pageArg = $location.search().page;
    $scope.search = {
      cohort: {
        id: null,
        name: null,
        isOwnedByCurrentUser: null
      },
      pagination: {
        currentPage: pageArg ? parseInt(pageArg, 10) : 1,
        itemsPerPage: 50
      },
      orderBy: cohortService.getSortByOptionsForSearch(),
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
      validationService.validateName({id: $scope.search.cohort.id, name: cohortName}, function(error) {
        if (error) {
          $scope.renameMode.error = errorHandler(error);
        } else {
          filteredCohortFactory.update($scope.search.cohort.id, cohortName, null, null, _.noop).then(function() {
            $scope.search.cohort.name = cohortName;
            exitRenameMode();
          }).catch(errorHandler);
        }
      });
    };

    var resetAddressBar = function(cohort) {
      $location.url($location.path());
      $location.search('id', cohort.id);
      $location.search('details', _.toString($scope.filtersVisible));
      $location.search('orderBy', $scope.search.orderBy.selected);
      $location.search('page', $scope.search.pagination.currentPage);

      $rootScope.pageTitle = cohort.name;
    };

    var updateAddressBar = function(currentPage, filterCriteria, definitions) {
      $location.search('page', currentPage);

      if (!_.isNil(filterCriteria)) {
        _.each(filterCriteria, function(value, key) {
          var definition = _.find(definitions, ['key', key]);
          if (definition && _.size(typeof value === 'boolean' ? _.toString(value) : value)) {
            $location.search(definition.param, value);
          }
        });
      }
    };

    var makeFiltersVisible = $scope.makeFiltersVisible = function(show, defaultValue) {
      var filtersVisible = _.isNil(show) ? defaultValue : utilService.toBoolOrNull(show);
      $location.search('details', _.toLower(filtersVisible));
      $scope.filtersVisible = filtersVisible;
      $scope.filterVisibilityToggled = true;
    };

    var getFilterCriteriaFromLocation = function(definitions) {
      var queryArgs = _.clone($location.search());
      var filterCriteria = {};

      _.each(definitions, function(d) {
        filterCriteria[d.key] = cohortUtils.translateQueryArg(d, queryArgs[d.param]);
      });
      return filterCriteria;
    };

    var render = function(cohort, filterCriteria, students, totalStudentCount) {
      if (cohort || filterCriteria) {
        _.extend($scope.search, {
          cohort: _.pick(cohort, ['id', 'name', 'isOwnedByCurrentUser']),
          filterCriteria: filterCriteria,
          results: {
            students: students,
            totalStudentCount: totalStudentCount
          }
        });
        $rootScope.pageTitle = $scope.search.cohort.name || 'Filtered Cohort';

      } else {
        $rootScope.pageTitle = 'Create a Filtered Cohort';
        makeFiltersVisible(true);
      }
      page.loading(false);
    };

    var init = $scope.nextPage = function(searchCriteria, offsetOverride, limitOverride) {
      // This function is invoked via 'Apply' button or pagination click.
      page.loading(true);
      $anchorScroll();

      filteredCohortFactory.getFilterCategories().then(function(response) {
        var filterCategories = $scope.filterCategories = response.data;
        var filterDefinitions = _.flatten(filterCategories);
        var criteria = searchCriteria || getFilterCriteriaFromLocation(filterDefinitions) || null;
        var isSearching = $scope.isSearching = !!_.find(_.values(criteria));
        var currentPage = $scope.search.pagination.currentPage;
        var queryArgs = _.clone($location.search());
        var limit = limitOverride || $scope.search.pagination.itemsPerPage;
        var offset = _.isNil(offsetOverride) ? (currentPage - 1) * limit : offsetOverride;

        if (queryArgs.orderBy && _.find($scope.search.orderBy.options, ['value', queryArgs.orderBy])) {
          $scope.search.orderBy.selected = queryArgs.orderBy;
        }
        updateAddressBar(currentPage);
        makeFiltersVisible(queryArgs.details, !!isSearching);
        // Get cohort metadata and students.
        async.series([
          function(callback) {
            var cohortId = parseInt($location.search().id, 10);

            if (cohortId) {
              var includeStudents = !isSearching;
              // If user 'isSearching' then we ignore the cohort's stored filterCriteria. We get students per 'criteria'.
              filteredCohortFactory.getCohort(cohortId, includeStudents, $scope.search.orderBy.selected, offset, limit).then(function(response2) {
                var cohort = response2.data;
                resetAddressBar(cohort);
                callback(null, cohort);

              }).catch(function(err) {
                callback(err);
              });

            } else {
              callback();
            }
          }
        ],
        function(err, data) {
          if (err) {
            errorHandler(err);

          } else {
            // If getCohort() was invoked above then the result is in 'data'.
            var cohort = data.length ? data[0] : null;

            if (isSearching) {
              studentFactory.getStudents(criteria, $scope.search.orderBy.selected, offset, limit).then(function(response3) {
                var students = response3.data.students;
                var totalStudentCount = response3.data.totalStudentCount;
                // If cohort.id is present then the 'Save' button will update cohort with this latest search criteria.
                cohort = {
                  id: _.get(cohort, 'id'),
                  name: _.get(cohort, 'name') || $location.search().name || cohortService.getSearchPageTitle(criteria),
                  isOwnedByCurrentUser: _.get(cohort, 'isOwnedByCurrentUser')
                };
                updateAddressBar($scope.search.pagination.currentPage, criteria, filterDefinitions);
                render(cohort, criteria, students, totalStudentCount);

              }).catch(errorHandler);

            } else if (cohort) {
              render(cohort, cohort.filterCriteria, cohort.students, cohort.totalStudentCount);
            } else {
              // Create new cohort mode.
              render();
            }
          }
        });
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
      applyFilters: function(filterCriteria) {
        $scope.search.pagination.currentPage = 1;
        init(filterCriteria);
      },
      onDelete: function() {
        $state.go('home');
      },
      onSave: function(cohort) {
        // Do not reload the page
        $scope.search.cohort = _.pick(cohort, ['id', 'name', 'isOwnedByCurrentUser']);
        resetAddressBar(cohort);
      }
    };

    init();

  });
}(window.angular));
