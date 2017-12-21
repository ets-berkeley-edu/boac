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

    var getGpaRanges = function() {
      return [
        {
          name: '3.50 - 4.00',
          value: 'numrange(3.5, 4, \'[]\')'
        },
        {
          name: '3.00 - 3.49',
          value: 'numrange(3, 3.5, \'[)\')'
        },
        {
          name: '2.50 - 2.99',
          value: 'numrange(2.5, 3, \'[)\')'
        },
        {
          name: '2.00 - 2.49',
          value: 'numrange(2, 2.5, \'[)\')'
        },
        {
          name: 'Below 2.0',
          value: 'numrange(0, 2, \'[)\')'
        }
      ];
    };

    var getStudentLevels = function() {
      return [
        {name: 'Freshman'},
        {name: 'Sophomore'},
        {name: 'Junior'},
        {name: 'Senior'}
      ];
    };

    var appendArrayArgs = function(apiPath, paramName, values) {
      var result = apiPath;
      _.each(values, function(value) {
        result += '&' + paramName + '=' + value;
      });
      return result;
    };

    var getStudents = function(gpaRanges, groupCodes, levels, majors, unitRangesEligibility, unitRangesPacing, orderBy, offset, limit) {
      var params = {
        offset: offset || 0,
        limit: limit || 50,
        orderBy: orderBy || 'first_name'
      };
      var apiPath = utilService.format('/api/students?offset=${offset}&limit=${limit}&orderBy=${orderBy}', params);
      apiPath = appendArrayArgs(apiPath, 'gpaRanges', gpaRanges);
      apiPath = appendArrayArgs(apiPath, 'groupCodes', groupCodes);
      apiPath = appendArrayArgs(apiPath, 'levels', levels);
      apiPath = appendArrayArgs(apiPath, 'majors', majors);
      apiPath = appendArrayArgs(apiPath, 'unitRangesEligibility', unitRangesEligibility);
      apiPath = appendArrayArgs(apiPath, 'unitRangesPacing', unitRangesPacing);
      return $http.get(apiPath);
    };
    return {
      analyticsPerUser: analyticsPerUser,
      getAllStudents: getAllStudents,
      getGpaRanges: getGpaRanges,
      getStudentLevels: getStudentLevels,
      getStudents: getStudents
    };
  });

}(window.angular));
