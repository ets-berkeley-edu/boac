(function(angular) {

  'use strict';

  angular.module('boac').controller('StudentController', function(analyticsFactory, $scope, $stateParams) {

    $scope.student = {
      canvasProfile: null,
      courses: null
    };

    analyticsFactory.analyticsPerUser($stateParams.uid).then(function(analytics) {
      $scope.student = analytics.data;
    });
  });

}(window.angular));
