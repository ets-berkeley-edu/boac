(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('cohortFactory', function($http) {

    var getCohorts = function() {
      return $http.get('/api/cohorts');
    };

    var getCohortDetails = function(code) {
      return $http.get('/api/cohort/' + code);
    };

    return {
      getCohorts: getCohorts,
      getCohortDetails: getCohortDetails
    };
  });

}(window.angular));
