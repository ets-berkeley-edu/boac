(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(authService, cohortFactory, cohortService, $scope, $state, $stateParams) {

    $scope.isLoading = true;

    $scope.search = {
      options: {
        teams: []
      },
      selected: {
        teams: []
      },
      results: {
        rows: null,
        totalCount: null
      },
      watch: {
        teamCode: null
      }
    };

    $scope.orderBy = {
      options: [{value: 'member_name', label: 'Name'}, {value: 'member_uid', label: 'UID'}],
      selected: 'member_name'
    };

    // More info: https://angular-ui.github.io/bootstrap/
    $scope.pagination = {
      currentPage: 0,
      itemsPerPage: 50
    };

    var goToUserPage = function(uid) {
      $state.go('user', {uid: uid});
    };

    var parseCohortFeed = function(response) {
      var cohort = response.data;
      // Search results are member list of the cohort
      $scope.search.results.totalCount = cohort.totalMemberCount;
      $scope.search.results.rows = cohort.members;

      // Plot the cohort
      var partitionedMembers = _.partition(cohort.members, function(member) {
        return _.isFinite(_.get(member, 'analytics.pageViews'));
      });
      // Render graph
      $scope.membersWithoutData = partitionedMembers[1];
      cohortService.displayCohort(partitionedMembers[0], goToUserPage);

      return cohort;
    };

    var refreshCohortView = function(callback) {
      var page = $scope.pagination.currentPage;
      var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;
      cohortFactory.getCohort($stateParams.code, $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(
        function(response) {
          $scope.cohort = parseCohortFeed(response);
          return callback($scope.cohort);
        },
        function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
          return callback(null);
        }
      );
    };

    var refreshSearchForm = function(teamCodes) {
      $scope.search.options.teams = _.reject($scope.search.options.teams, function(team) {
        var isSelectedTeam = _.includes(teamCodes, team.code);
        if (isSelectedTeam) {
          $scope.search.selected.teams.push(team);
        }
        return isSelectedTeam;
      });
    };

    var refreshResults = function() {
      if ($scope.cohort) {
        refreshCohortView(angular.noop);
      } else {
        var teamCodes = _.map($scope.search.selected.teams, 'code');
        var page = $scope.pagination.currentPage;
        var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;
        cohortFactory.getTeamsMembers(teamCodes, $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(parseCohortFeed,
          function(err) {
            $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
            return callback(null);
          }
        );
      }
    };

    $scope.createCohort = function(label) {
      $scope.isLoading = true;
      // This function is invoked from template
      if ($scope.search.selected.teams) {
        cohortFactory.createCohort(label, $scope.search.selected.teams).then(function(response) {
          $scope.cohort = response.data;
          $scope.isLoading = false;
          $scope.pagination.currentPage = 0;
        });
      }
    };

    $scope.nextPage = function() {
      refreshResults();
    };

    $scope.$watch('search.watch.teamCode', function(value) {
      if (value) {
        $scope.cohort = null;
        refreshSearchForm([ $scope.search.watch.teamCode ]);
        refreshResults();
      }
    }, true);

    $scope.$watch('orderBy.selected', function(value) {
      if (value && value !== $scope.orderBy.selected) {
        $scope.pagination.currentPage = 0;
        refreshResults();
      }
    });

    var init = function() {
      cohortFactory.getTeams().then(function(teams) {
        // Populate search form
        $scope.search.options.teams = teams.data;

        // if code is "0" then we offer a blank slate, the first step in creating a new cohort.
        if ($stateParams.code === '0') {
          $scope.isLoading = false;
        } else {
          $scope.selectedTab = 'list';

          refreshCohortView(function(cohort) {
            refreshSearchForm(_.map(cohort.teams, 'code'));
            // Done!
            $scope.isLoading = false;
          });
        }
      });
    };

    authService.authWrap(init)();

  });
}(window.angular));
