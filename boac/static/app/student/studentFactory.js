(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('studentFactory', function($http) {

    var analyticsPerUser = function(uid) {
      return $http.get('/api/user/' + uid + '/analytics');
    };

    var getAllStudents = function(orderBy) {
      return $http({
        url: '/api/students/all',
        method: 'GET',
        params: orderBy ? {orderBy: orderBy} : {}
      });
    };

    return {
      analyticsPerUser: analyticsPerUser,
      getAllStudents: getAllStudents
    };
  });

}(window.angular));
