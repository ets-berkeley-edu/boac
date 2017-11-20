(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function($http, $rootScope) {

    var createCohort = function(label, teamCodes) {
      var args = {
        label: label,
        teamCodes: teamCodes
      };
      return $http.post('/api/cohort/create', args).then(function() {
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
      getTeams: getTeams,
      updateCohort: updateCohort
    };
  });

}(window.angular));
