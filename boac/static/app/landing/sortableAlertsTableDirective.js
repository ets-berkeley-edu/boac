(function(angular) {

  'use strict';

  angular.module('boac').directive('sortableAlertsTable', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {
        alerts: '=',
        watchlist: '='
      },

      templateUrl: '/static/app/landing/sortableAlertsTable.html',

      link: function(scope) {
        scope.sort = function(data, sortBy) {
          if (data.sortBy === sortBy) {
            data.reverse = !data.reverse;
          } else {
            data.sortBy = sortBy;
            data.reverse = false;
          }
        };
      }
    };
  });

}(window.angular));
