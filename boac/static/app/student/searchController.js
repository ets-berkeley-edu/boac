(function(angular) {

  'use strict';

  angular.module('boac').controller('SearchController', function(authService, cohortFactory, $scope) {

    $scope.search = {
      isLoading: true,
      options: {
        teams: []
      },
      results: []
    };

    $scope.selected = {
      teams: []
    };

    $scope.watch = {
      teamCode: null
    };

    $scope.$watch('search.watch.teamCode', function() {
      var code = $scope.watch.teamCode;
      if (code) {
        cohortFactory.getTeam(code).then(function(response) {
          var team = response.data;
          $scope.search.results = team.members;
          $scope.selected.teams.push(code);
        });
      }
    }, true);

    $scope.createCohort = function(label) {
      $scope.isLoading = true;
      if ($scope.selected.teams) {
        cohortFactory.createCohort(label, $scope.selected.teams).then(function(teams) {
          $scope.search.teams = teams;
          $scope.search.isLoading = false;
        });
      }
    };

    var init = function() {
      $scope.search.isLoading = true;

      cohortFactory.getTeams().then(function(teams) {
        $scope.search.options.teams = teams.data;
        $scope.search.isLoading = false;
      });
    };

    authService.authWrap(init)();
  });

}(window.angular));
