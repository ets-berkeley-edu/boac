(function(angular) {

  'use strict';

  angular.module('boac').directive('courseSiteMetrics', function() {
    return {
      restrict: 'E',
      scope: {
        canvasSite: '=',
        courseName: '=',
        drawBoxplot: '=',
        termId: '='
      },
      templateUrl: '/static/app/student/courseSiteMetrics.html',
      link: function(scope) {
        scope.metrics = [
          {
            dataset: scope.canvasSite.analytics.assignmentsOnTime,
            id: 'assignmentsOnTime',
            label: 'Assignments on Time',
            missingLabel: 'No Assignments'
          },
          {
            dataset: scope.canvasSite.analytics.courseCurrentScore,
            id: 'courseCurrentScore',
            label: 'Assignment Grades',
            missingLabel: 'No Grades'
          },
          {
            dataset: scope.canvasSite.analytics.pageViews,
            id: 'pageViews',
            label: 'Page Views',
            missingLabel: 'No Page Views'
          }
        ];
      }
    };
  });

}(window.angular));
