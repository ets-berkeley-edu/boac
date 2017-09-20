(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('analyticsFactory', function($http) {

    var analyticsPerUser = function(uid) {
      return $http.get('/api/user/' + uid + '/analytics');
    };

    return {
      analyticsPerUser: analyticsPerUser
    };
  });

}(window.angular));
