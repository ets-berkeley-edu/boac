(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('studentFactory', function(utilService, $http) {

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

    var getStudents = function(groupCodes, orderBy, offset, limit) {
      var params = {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/students?offset=${offset}&limit=${limit}&orderBy=${orderBy}', params);
      _.each(groupCodes, function(groupCode) {
        apiPath += '&groupCodes=' + groupCode;
      });
      return $http.get(apiPath);
    };

    return {
      analyticsPerUser: analyticsPerUser,
      getAllStudents: getAllStudents,
      getStudents: getStudents
    };
  });

}(window.angular));
