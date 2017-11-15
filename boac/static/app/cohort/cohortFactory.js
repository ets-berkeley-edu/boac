(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function($http) {

    var createCohort = function(label, teamCodes) {
      var args = {
        label: label,
        teamCodes: teamCodes
      };
      return $http.post('/api/cohort/create', args);
    };

    var deleteCohort = function(id) {
      return $http.delete('/api/cohort/delete/' + id);
    };

    var getAll = function() {
      return $http.get('/api/cohorts/all');
    };

    var getCohort = function(code) {
      return $http.get('/api/cohort/' + code);
    };

    var getMyCohorts = function() {
      return $http.get('/api/cohorts/my');
    };

    var getTeams = function() {
      return $http.get('/api/teams');
    };

    var updateCohort = function(id, label) {
      var args = {
        id: id,
        label: label
      };
      return $http.post('/api/cohort/update', args);
    };

    return {
      createCohort: createCohort,
      deleteCohort: deleteCohort,
      getAll: getAll,
      getCohort: getCohort,
      getMyCohorts: getMyCohorts,
      getTeams: getTeams,
      updateCohort: updateCohort
    };
  });

}(window.angular));
