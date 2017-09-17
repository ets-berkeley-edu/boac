(function(angular) {

  'use strict';

  angular.module('boac').controller('StudentController', function(analyticsFactory, $scope, $stateParams) {

    var loadAnalytics = function() {
      $scope.student.isLoading = true;
      analyticsFactory.analyticsPerUser($stateParams.uid).then(function(analytics) {
        $scope.student = analytics.data;
      }).catch(function(error) {
        $scope.error = _.truncate(error.message, {length: 200});
      }).then(function() {
        $scope.student.isLoading = false;
      });
    };

    $scope.student = {
      canvasProfile: null,
      courses: null,
      isLoading: true
    };

    loadAnalytics();
  });

}(window.angular));
