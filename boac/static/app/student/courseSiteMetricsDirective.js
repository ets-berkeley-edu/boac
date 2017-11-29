(function(angular) {

  'use strict';

  angular.module('boac').directive('courseSiteMetrics', function() {
    return {
      restrict: 'E',
      scope: {
        canvasSite: '=',
        ccn: '=',
        drawBoxplot: '=',
        percentile: '=',
        termId: '='
      },
      templateUrl: '/static/app/student/courseSiteMetrics.html'
    };
  });

}(window.angular));
