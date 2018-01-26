(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('studentFactory', function(utilService, $http) {

    var analyticsPerUser = function(uid) {
      return $http.get('/api/user/' + uid + '/analytics');
    };

    var dismissAlert = function(alertId) {
      return $http.get('/api/alerts/' + alertId + '/dismiss');
    };

    var getAlerts = function(sid) {
      return $http.get('/api/alerts/current/' + sid);
    };

    var getAllStudents = function(orderBy) {
      return $http({
        url: '/api/students/all',
        method: 'GET',
        params: orderBy ? {orderBy: orderBy} : {}
      });
    };

    var getGpaRanges = function() {
      return [
        {name: '3.50 - 4.00', value: 'numrange(3.5, 4, \'[]\')'},
        {name: '3.00 - 3.49', value: 'numrange(3, 3.5, \'[)\')'},
        {name: '2.50 - 2.99', value: 'numrange(2.5, 3, \'[)\')'},
        {name: '2.00 - 2.49', value: 'numrange(2, 2.5, \'[)\')'},
        {name: 'Below 2.0', value: 'numrange(0, 2, \'[)\')'}
      ];
    };

    var getRelevantMajors = function() {
      return $http.get('/api/majors/relevant');
    };

    var getStudentLevels = function() {
      return [
        {name: 'Freshman'},
        {name: 'Sophomore'},
        {name: 'Junior'},
        {name: 'Senior'}
      ];
    };

    var getUnitRangesEligibility = function() {
      return [
        {name: '0 - 5', value: 'numrange(0, 5, \'[]\')'},
        {name: '6 - 11', value: 'numrange(6, 11, \'[]\')'},
        {name: '12 - 17', value: 'numrange(12, 17, \'[]\')'},
        {name: '18 - 23', value: 'numrange(18, 23, \'[]\')'},
        {name: '24 - 29', value: 'numrange(24, 29, \'[]\')'},
        {name: '30 +', value: 'numrange(30, NULL, \'[)\')'}
      ];
    };

    var getUnitRangesPacing = function() {
      return [
        {name: '0 - 29', value: 'numrange(0, 30, \'[)\')'},
        {name: '30 - 59', value: 'numrange(30, 60, \'[)\')'},
        {name: '60 - 89', value: 'numrange(60, 90, \'[)\')'},
        {name: '90 - 119', value: 'numrange(90, 120, \'[)\')'},
        {name: '120 +', value: 'numrange(120, NULL, \'[)\')'}
      ];
    };

    var getStudents = function(gpaRanges, groupCodes, levels, majors, unitRangesEligibility, unitRangesPacing, orderBy, offset, limit) {
      var args = {
        gpaRanges: gpaRanges || [],
        groupCodes: groupCodes || [],
        levels: levels || [],
        majors: majors || [],
        unitRangesEligibility: unitRangesEligibility || [],
        unitRangesPacing: unitRangesPacing || [],
        orderBy: orderBy || 'first_name',
        offset: offset || 0,
        limit: limit || 50
      };
      return $http.post('/api/students', args);
    };

    return {
      analyticsPerUser: analyticsPerUser,
      dismissAlert: dismissAlert,
      getAlerts: getAlerts,
      getAllStudents: getAllStudents,
      getGpaRanges: getGpaRanges,
      getRelevantMajors: getRelevantMajors,
      getStudentLevels: getStudentLevels,
      getStudents: getStudents,
      getUnitRangesEligibility: getUnitRangesEligibility,
      getUnitRangesPacing: getUnitRangesPacing
    };
  });

}(window.angular));
