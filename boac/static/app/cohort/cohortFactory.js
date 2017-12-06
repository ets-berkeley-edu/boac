(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function(googleAnalyticsService, $http, $rootScope) {

    var createCohort = function(label, teamGroupCodes) {
      var args = {
        label: label,
        teamGroupCodes: teamGroupCodes
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
      });
    };

    var getAll = function() {
      return $http.get('/api/cohorts/all');
    };

    var getCohort = function(id, orderBy, offset, limit) {
      return $http.post('/api/cohort/' + id, {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'member_name'
      });
    };

    var getMyCohorts = function() {
      return $http.get('/api/cohorts/my');
    };

    var getTeam = function(code, orderBy, offset, limit) {
      return $http.post('/api/team/' + code, {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'member_name'
      });
    };

    var getTeamGroupsMembers = function(teamGroupCodes, orderBy, offset, limit) {
      return $http.post('/api/team_groups/members', {
        teamGroupCodes: teamGroupCodes,
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'member_name'
      });
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
      getMyCohorts: getMyCohorts,
      getTeam: getTeam,
      getTeams: getTeams,
      getTeamGroupsMembers: getTeamGroupsMembers,
      updateCohort: updateCohort
    };
  });

}(window.angular));
