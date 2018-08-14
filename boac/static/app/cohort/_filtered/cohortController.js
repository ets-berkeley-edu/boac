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
    $location,
    $rootScope,
    $scope,
    cohortService,
    filterCriteriaService,
    filteredCohortFactory,
    page,
    studentFactory,
    studentSearchService,
    validationService
  ) {

    $scope.orderBy = studentSearchService.getSortByOptionsForSearch();
    $scope.hasFilterCriteria = false;
    $scope.tab = 'list';

    $scope.filterCriteriaComponent = {
      filters: {
        added: null
      }
    };

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

    var errorHandler = function(error) {
      if (error.status === 404) {
        $location.replace().path('/404');
      } else {
        $scope.error = validationService.parseError(error);
        page.loading(false);
      }
    };

    $scope.rename = function(cohortName) {
      validationService.validateName({id: $scope.cohort.id, name: cohortName}, function(error) {
        if (error) {
          errorHandler(error);
        } else {
          filteredCohortFactory.rename($scope.cohort.id, cohortName).then(function() {
            cohort.name = cohortName;
          }).catch(errorHandler);
        }
      });
    };

    var loadSavedCohort = function(cohortId, orderBy, offset, limit) {
      filteredCohortFactory.getCohort(cohortId, orderBy, offset, limit).then(function(response) {
        var cohort = $scope.cohort = response.data;
        $rootScope.pageTitle = $scope.cohortName = cohort.name;

        // Update browser location
        $location.url($location.path());
        $location.search('c', cohort.id);

        _.extend($scope.search, {
          filterCriteria: cohort.filterCriteria,
          results: {
            students: cohort.students,
            totalStudentCount: cohort.totalStudentCount
          }
        });
        page.loading(false);
      }).catch(errorHandler);
    };

    var search = function(filterCriteria, orderBy, offset, limit) {
      filterCriteriaService.updateLocation(filterCriteria, $scope.search.pagination.currentPage);
      studentFactory.getStudents(filterCriteria, orderBy, offset, limit).then(function(response) {
        $scope.cohortName = $location.search().cohortName;
        $scope.cohortName = $scope.cohortName || cohortService.getSearchPageTitle(filterCriteria);
        $rootScope.pageTitle = $scope.cohortName || 'Filtered Cohort';
        _.extend($scope.search, {
          filterCriteria: filterCriteria,
          results: {
            students: response.data.students,
            totalStudentCount: response.data.totalStudentCount
          }
        });
        page.loading(false);
      }).catch(errorHandler);
    };

    var any = (criteria) => _.find(_.values(criteria));

    var reload = $scope.reload = function(criteria, offsetOverride, limitOverride) {
      page.loading(true);

      var orderBy = $scope.search.orderBy.selected;
      var limit = limitOverride || $scope.search.pagination.itemsPerPage;
      var offset = offsetOverride === null ? ($scope.search.pagination.currentPage - 1) * limit : offsetOverride;
      var hasFilterCriteria = $scope.hasFilterCriteria = criteria && any(criteria);

      if (hasFilterCriteria) {
        search(criteria, orderBy, offset, limit);

      } else {
        var cohortId = filterCriteriaService.getCohortIdFromLocation();

        if (cohortId > 0) {
          $scope.hasFilterCriteria = true;
          loadSavedCohort(cohortId, orderBy, offset, limit);

        } else {
          var filterCriteria = filterCriteriaService.getFilterCriteriaFromLocation();

          if (any(filterCriteria)) {
            search(filterCriteria);

          } else {
            // No query args is create-cohort mode
            $scope.detailsShowing = true;
            $rootScope.pageTitle = 'Create a Filtered Cohort';
            page.loading(false);
          }
        }
      }
    };

    $scope.showHideDetails = function(detailsShowing) {
      $scope.detailsShowing = !detailsShowing;
    };

    $scope.nextPage = function() {
      reload();
    };

    $scope.onTab = function(tabType) {
      if (tabType === 'matrix') {
        reload(null, 0, Number.MAX_SAFE_INTEGER);
      } else {
        reload();
      }
      $location.search('tab', tabType);
    };

    var init = function() {
      reload();
    };

    init();

  });
}(window.angular));
