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

  boac.factory('cohortFactory', function(googleAnalyticsService, utilService, $http, $rootScope) {

    var createCohort = function(label, gpaRanges, groupCodes, levels, majors, unitRanges, intensive, inactive) {
      var args = {
        label: label,
        gpaRanges: gpaRanges,
        groupCodes: groupCodes,
        levels: levels,
        majors: majors,
        unitRanges: unitRanges
      };
      if (utilService.toBoolOrNull(intensive)) {
        args.inIntensiveCohort = true;
      }
      if (utilService.toBoolOrNull(inactive)) {
        args.isInactive = true;
      }
      return $http.post('/api/cohort/create', args).then(function(response) {
        var cohort = response.data;
        $rootScope.$broadcast('cohortCreated', {
          cohort: cohort
        });
        $rootScope.$broadcast('myCohortsUpdated');
        // Track the event
        googleAnalyticsService.track('cohort', 'create', cohort.label, cohort.id);
      });
    };

    var deleteCohort = function(cohort) {
      return $http.delete('/api/cohort/delete/' + cohort.id).then(function() {
        $rootScope.$broadcast('myCohortsUpdated');
        $rootScope.$broadcast('cohortDeleted', {
          cohort: cohort
        });
      });
    };

    var getAll = function() {
      return $http.get('/api/cohorts/all');
    };

    var getCohort = function(id, orderBy, offset, limit) {
      var params = {
        id: id,
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/cohort/${id}?offset=${offset}&limit=${limit}&orderBy=${orderBy}', params);
      return $http.get(apiPath);
    };

    var getMyCohorts = function() {
      return $http.get('/api/cohorts/my');
    };

    var getTeam = function(code, orderBy) {
      var params = {
        code: code,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/team/${code}?orderBy=${orderBy}', params);
      return $http.get(apiPath);
    };

    var getTeams = function() {
      return $http.get('/api/teams/all');
    };

    var getAllTeamGroups = function() {
      return $http.get('/api/team_groups/all');
    };

    var changeCohortName = function(id, label) {
      var args = {
        id: id,
        label: label
      };
      return $http.post('/api/cohort/update', args).then(function(response) {
        $rootScope.$broadcast('myCohortsUpdated');
        $rootScope.$broadcast('cohortNameChanged', {
          cohort: response.data
        });
      });
    };

    return {
      createCohort: createCohort,
      deleteCohort: deleteCohort,
      getAll: getAll,
      getAllTeamGroups: getAllTeamGroups,
      getCohort: getCohort,
      getMyCohorts: getMyCohorts,
      getTeam: getTeam,
      getTeams: getTeams,
      changeCohortName: changeCohortName
    };
  });

}(window.angular));
