(function(angular) {

  'use strict';

  angular.module('boac').directive('studentAlertMessage', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {
        alert: '='
      },
      templateUrl: '/static/app/student/studentAlertMessage.html'
    };
  });

}(window.angular));
