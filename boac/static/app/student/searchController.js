(function(angular) {

  'use strict';

  angular.module('boac').controller('SearchController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.search = {
      isLoading: true,
      criteria: {
        teams: []
      },
      options: {
        teams: null
      },
      select: {
        teamCode: null
      },
      results: []
    };

    $scope.$watch('search.select.teamCode', function() {
      var teamCode = $scope.search.select.teamCode;
      if (teamCode) {
        cohortFactory.getCohortDetails(teamCode).then(function(response) {
          $scope.search.results = response.data.members;
        });
      }
    }, true);

    var loadTeams = function() {
      $scope.isLoading = true;

      cohortFactory.getTeams().then(function(teams) {
        $scope.search.options.teams = teams.data;
        $scope.search.isLoading = false;
      });
    };

    var init = authService.authWrap(loadTeams);

    init();
  });

}(window.angular));
