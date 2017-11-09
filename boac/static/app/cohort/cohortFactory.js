(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function($http) {

    var getTeams = function() {
      return $http.get('/api/teams');
    };

    var getCohortDetails = function(code) {
      return $http.get('/api/cohort/' + code);
    };

    return {
      getTeams: getTeams,
      getCohortDetails: getCohortDetails
    };
  });

}(window.angular));
