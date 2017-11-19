(function(angular) {

  'use strict';

  angular.module('boac').directive('cohortsDropdown', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {},
      templateUrl: '/static/app/cohort/dropdownNav.html',
      controller: function(cohortFactory, $rootScope, $scope) {

        $scope.myCohorts = null;

        var init = function() {
          cohortFactory.getMyCohorts().then(function(response) {
            $scope.myCohorts = response.data;
          });
        };

        $rootScope.$on('myCohortsUpdated', init);

        init();
      }
    };
  });

}(window.angular));
