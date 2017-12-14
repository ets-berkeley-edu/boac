(function(angular) {

  'use strict';

  angular.module('boac').directive('myCohortsDropdown', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {},
      templateUrl: '/static/app/cohort/myCohortsDropdown.html',
      controller: function(cohortFactory, $rootScope, $scope) {

        $scope.isLoading = true;
        $scope.myCohorts = null;
        $scope.truncate = _.truncate;

        var init = function() {
          cohortFactory.getMyCohorts().then(function(response) {
            $scope.myCohorts = response.data;
            $scope.isLoading = false;
          });
        };

        $rootScope.$on('myCohortsUpdated', init);

        init();
      }
    };
  });

}(window.angular));
