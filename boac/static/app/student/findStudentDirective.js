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
          return studentFactory.getAllStudents('groupName').then(function(response) {
            var options = [];
            _.each(response.data, function(student) {
              _.each(student.athletics, function(a) {
                options.push({
                  uid: student.uid,
                  name: student.name + ' - ' + student.sid,
                  groupName: a.groupName
                });
              });
            });
            return options;
          });
        };

        var studentOptions = null;

        $scope.lazyLoadOptions = function() {
          if (!studentOptions) {
            var deferred = $q.defer();
            studentOptions = deferred.promise;

            $timeout(function() {
              loadOptions().then(deferred.resolve);
            }, 1000);
          }

          return studentOptions;
        };
      }
    };
  });

}(window.angular));
