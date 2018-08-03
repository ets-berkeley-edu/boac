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
    filteredCohortFactory,
    page,
    studentFactory,
    studentSearchService,
    utilService,
    validationService
  ) {

    var args = _.clone($location.search());

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

    $scope.search = {
      criteria: {
        advisorLdapUid: args.a,
        gpaRanges: utilService.arrayRequired(args.g),
        groupCodes: utilService.arrayRequired(args.t),
        intensive: args.i,
        inactive: args.v,
        levels: utilService.arrayRequired(args.l),
        majors: utilService.arrayRequired(args.m),
        unitRanges: utilService.arrayRequired(args.u)
      },
      orderBy: studentSearchService.getSortByOptionsForSearch(),
      pagination: studentSearchService.initPagination(),
      results: {
        students: [],
        totalStudentCount: null
      }
    };

    var nextPage = $scope.nextPage = function() {
      page.loading(true);
      var cohortId = parseInt(args.c, 10);
      var orderBy = $scope.search.orderBy.selected;
      var limit = $scope.search.pagination.itemsPerPage;
      var offset = ($scope.search.pagination.currentPage - 1) * limit;

      if (cohortId > 0) {
        filteredCohortFactory.getCohort(cohortId, orderBy, offset, limit).then(function(response) {
          var cohort = response.data;
          $scope.cohort = cohort;
          $scope.search.criteria = cohort.filterCriteria;
          $scope.search.results = {
            students: cohort.students,
            totalStudentCount: cohort.totalStudentCount
          };
          $rootScope.pageTitle = $scope.cohortName = cohort.name;
          page.loading(false);

        }).catch(errorHandler);

      } else {
        studentFactory.getStudents($scope.search.criteria, orderBy, offset, limit).then(function(response) {
          $scope.search.results = {
            students: response.data.students,
            totalStudentCount: response.data.totalStudentCount
          };
          $scope.cohortName = cohortService.getSearchPageTitle($scope.search.criteria);
          $rootScope.pageTitle = $scope.cohortName || 'Filtered Cohort';
          page.loading(false);

        }).catch(errorHandler);
      }
    };

    nextPage();
  });
}(window.angular));
