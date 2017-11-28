(function(angular) {

  'use strict';

  angular.module('boac').directive('findStudent', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {},
      templateUrl: '/static/app/student/findStudentSelect.html',
      controller: function(studentFactory, $location, $q, $scope, $timeout) {

        $scope.$watch('selectedUID', function() {
          if (!_.isEmpty($scope.selectedUID)) {
            $location.path('/student/' + $scope.selectedUID);
            $location.replace();
          }
        });

        var loadOptions = function() {
          return studentFactory.getAllStudents('teamCode').then(function(response) {
            return response.data;
          });
        };

        $scope.lazyLoadOptions = function() {
          var deferred = $q.defer();

          $timeout(function() {
            loadOptions().then(deferred.resolve);
          }, 1000);

          return deferred.promise;
        };
      }
    };
  });

}(window.angular));
