(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function(googleAnalyticsService, utilService, $http, $rootScope) {

    var createCohort = function(label, gpaRanges, groupCodes, levels, majors, unitRanges) {
      var args = {
        label: label,
        gpaRanges: gpaRanges,
        groupCodes: groupCodes,
        levels: levels,
        majors: majors,
        unitRanges: unitRanges
      };
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

    var getIntensiveCohort = function(orderBy, offset, limit) {
      var params = {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/intensive_cohort?offset=${offset}&limit=${limit}&orderBy=${orderBy}', params);
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

    var updateCohort = function(id, label) {
      var args = {
        id: id,
        label: label
      };
      return $http.post('/api/cohort/update', args).then(function() {
        $rootScope.$broadcast('myCohortsUpdated');
      });
    };

    return {
      createCohort: createCohort,
      deleteCohort: deleteCohort,
      getAll: getAll,
      getAllTeamGroups: getAllTeamGroups,
      getCohort: getCohort,
      getIntensiveCohort: getIntensiveCohort,
      getMyCohorts: getMyCohorts,
      getTeam: getTeam,
      getTeams: getTeams,
      updateCohort: updateCohort
    };
  });

}(window.angular));
