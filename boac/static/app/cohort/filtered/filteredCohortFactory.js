/**
 * Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.
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

  angular.module('boac').factory('filteredCohortFactory', function($http, $rootScope, googleAnalyticsService) {

    var getStashedCohort = function(cohortId) {
      return _.find($rootScope.profile.myFilteredCohorts, ['id', cohortId]);
    };

    var createCohort = function(name, filterCriteria) {
      var args = _.merge({name: name}, filterCriteria);
      return $http.post('/api/cohort/create', args).then(function(response) {
        var cohort = response.data;
        $rootScope.profile.myFilteredCohorts.push(cohort);
        googleAnalyticsService.track('Filtered Cohort', 'create', cohort.name, cohort.id);
        return cohort;
      });
    };

    var deleteCohort = function(cohortId) {
      return $http.delete('/api/cohort/delete/' + cohortId).then(function() {
        $rootScope.profile.myFilteredCohorts = _.remove($rootScope.profile.myFilteredCohorts, function(cohort) {
          var match = cohort.id !== cohortId;
          if (match) {
            googleAnalyticsService.track('Filtered Cohort', 'delete', cohort.name, cohort.id);
          }
          return match;
        });
      });
    };

    var getAll = function() {
      return $http.get('/api/cohorts/all');
    };

    var getCohort = function(id, includeStudents, orderBy, offset, limit) {
      var template = _.template('/api/cohort/${id}?includeStudents=${includeStudents}&offset=${offset}&limit=${limit}&orderBy=${orderBy}');
      var args = {
        id: id,
        includeStudents: includeStudents || true,
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };

      return $http.get(template(args));
    };

    var getFilterCategories = function() {
      return $http.get('/api/menu/cohort/deprecated_filter_definitions');
    };

    var getStudentsWithAlertsInCohort = function(cohortId) {
      return $http.get('/api/cohort/' + cohortId + '/students_with_alerts');
    };

    var update = function(id, name, filterCriteria, studentCount, callback) {
      var args = {
        id: id,
        name: name,
        filterCriteria: filterCriteria,
        studentCount: studentCount
      };
      return $http.post('/api/cohort/update', args).then(function(response) {
        var cohort = response.data;
        var stashedCohort = getStashedCohort(id);

        stashedCohort.name = cohort.name;
        stashedCohort.totalStudentCount = cohort.totalStudentCount;
        googleAnalyticsService.track('Filtered Cohort', 'update', cohort.name, cohort.id);
        callback(cohort);
      });
    };

    return {
      createCohort: createCohort,
      deleteCohort: deleteCohort,
      getAll: getAll,
      getCohort: getCohort,
      getFilterCategories: getFilterCategories,
      getStudentsWithAlertsInCohort: getStudentsWithAlertsInCohort,
      update: update
    };
  });

}(window.angular));
