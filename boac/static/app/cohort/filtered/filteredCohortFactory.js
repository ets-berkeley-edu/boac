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

  var boac = angular.module('boac');

  boac.factory('filteredCohortFactory', function($http, $rootScope, googleAnalyticsService, utilService) {

    var createCohort = function(label, filterCriteria) {
      var args = _.merge({label: label}, filterCriteria);
      return $http.post('/api/filtered_cohort/create', args).then(function(response) {
        var cohort = response.data;
        $rootScope.$broadcast('filteredCohortCreated', {
          cohort: cohort
        });
        $rootScope.$broadcast('myFilteredCohortsUpdated');
        // Track the event
        googleAnalyticsService.track('cohort', 'create', cohort.name, cohort.id);
        return cohort;
      });
    };

    var deleteCohort = function(cohort) {
      return $http.delete('/api/filtered_cohort/delete/' + cohort.id).then(function() {
        $rootScope.$broadcast('myFilteredCohortsUpdated');
        $rootScope.$broadcast('filteredCohortDeleted', {
          cohort: cohort
        });
      });
    };

    var getAll = function() {
      return $http.get('/api/filtered_cohorts/all');
    };

    var getCohort = function(id, orderBy, offset, limit) {
      var params = {
        id: id,
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/filtered_cohort/${id}?offset=${offset}&limit=${limit}&orderBy=${orderBy}', params);
      return $http.get(apiPath);
    };

    var getFilterCategories = function() {
      return $http.get('/api/filter_cohort/definitions');
    };

    var getMyFilteredCohorts = function() {
      return $http.get('/api/filtered_cohorts/my');
    };

    var rename = function(id, label) {
      var args = {
        id: id,
        label: label
      };
      return $http.post('/api/filtered_cohort/rename', args).then(function(response) {
        $rootScope.$broadcast('myFilteredCohortsUpdated');
        $rootScope.$broadcast('filteredCohortNameChanged', {
          cohort: response.data
        });
      });
    };

    return {
      createCohort: createCohort,
      deleteCohort: deleteCohort,
      getAll: getAll,
      getCohort: getCohort,
      getFilterCategories: getFilterCategories,
      getMyFilteredCohorts: getMyFilteredCohorts,
      rename: rename
    };
  });

}(window.angular));
