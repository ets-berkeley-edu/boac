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

  angular.module('boac').controller('SearchController', function(
    config,
    studentFactory,
    studentSearchService,
    validationService,
    $location,
    $scope
  ) {

    $scope.demoMode = config.demoMode;

    $scope.pagination = {
      currentPage: 1,
      itemsPerPage: 50
    };

    $scope.orderBy = studentSearchService.getSortByOptionsForSearch();

    var nextPage = $scope.nextPage = function() {
      var page = $scope.pagination.currentPage;
      var offset = page < 2 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

      $scope.isLoading = true;
      studentFactory.searchForStudents($scope.search.phrase, $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(
        function(response) {
          $scope.search.results = response.data;
        },
        function(err) {
          $scope.error = validationService.parseError(err);
        }
      ).then(function() {
        $scope.isLoading = false;
      });
    };

    $scope.$watch('orderBy.selected', function(value) {
      if (value && !$scope.isLoading) {
        $location.search('o', $scope.orderBy.selected);
        $scope.pagination.currentPage = 1;
        nextPage();
      }
    });

    $scope.$watch('pagination.currentPage', function() {
      if (!$scope.isLoading) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    var init = function() {
      $scope.search = {
        phrase: $location.search().q,
        results: null
      };
      var args = _.clone($location.search());
      var offset = 0;

      if (args.o && _.find($scope.orderBy.options, ['value', args.o])) {
        $scope.orderBy.selected = args.o;
      }
      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
        offset = $scope.pagination.currentPage < 2 ? 0 : ($scope.pagination.currentPage - 1) * $scope.pagination.itemsPerPage;
      }
      if ($scope.search.phrase) {
        $scope.isLoading = true;
        studentFactory.searchForStudents($scope.search.phrase, $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(
          function(response) {
            $scope.search.results = response.data;
          },
          function(err) {
            $scope.error = validationService.parseError(err);
          }
        ).then(function() {
          $scope.isLoading = false;
        });
      } else {
        $scope.error = {message: 'No search input found.'};
      }
    };

    init();
  });

}(window.angular));
