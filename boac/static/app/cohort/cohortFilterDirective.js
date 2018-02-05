(function(angular) {

  'use strict';

  angular.module('boac').directive('cohortFilter', function(utilService) {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: true,
      templateUrl: '/static/app/cohort/cohortFilterDropdown.html',
      link: function(scope, elem, attrs) {
        scope.toggleFilter = function(event) {
          // Known issue: https://github.com/angular-ui/bootstrap/issues/6038
          if (event) {
            event.stopPropagation();
          }
        };
        scope.id = utilService.camelCaseToDashes(attrs.menuType);
        scope.isOpen = attrs.menuType + 'Open';
        scope.menuLabel = attrs.label;
        scope.menuType = attrs.menuType;
      }
    };
  });

}(window.angular));
