(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function($http, $rootScope) {

    var createCohort = function(label, teamCodes) {
      var args = {
        label: label,
        teamCodes: teamCodes
      };
      return $http.post('/api/cohort/create', args).then(function(response) {
        $rootScope.$broadcast('cohortCreated', {
          cohort: response.data
        });
        $rootScope.$broadcast('myCohortsUpdated');
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

    var getCohort = function(code, orderBy, offset, limit) {
      return $http.post('/api/cohort/' + code, {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'member_name'
      });
    };

    var getMyCohorts = function() {
      return $http.get('/api/cohorts/my');
    };

    var getTeamsMembers = function(teamCodes, orderBy, offset, limit) {
      return $http.post('/api/teams/members', {
        teamCodes: teamCodes,
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'member_name'
      });
    };

    var getTeams = function() {
      return $http.get('/api/teams');
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
      getCohort: getCohort,
      getMyCohorts: getMyCohorts,
      getTeamsMembers: getTeamsMembers,
      getTeams: getTeams,
      updateCohort: updateCohort
    };
  });

}(window.angular));
