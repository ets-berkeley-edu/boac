(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('studentFactory', function($http) {

    var analyticsPerUser = function(uid) {
      return $http.get('/api/user/' + uid + '/analytics');
    };

    var getAllStudents = function(sortBy) {
      return $http({
        url: '/api/students/all',
        method: 'GET',
        params: sortBy ? {sortBy: sortBy} : {}
      });
    };

    return {
      analyticsPerUser: analyticsPerUser,
      getAllStudents: getAllStudents
    };
  });

}(window.angular));
