(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(authService, cohortFactory, cohortService, $rootScope, $scope, $state, $stateParams) {

    $scope.isLoading = true;
    $scope.isMatrixLoading = false;

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
      enabled: true,
      currentPage: 0,
      itemsPerPage: 50
    };

    var parseCohortFeed = function(response) {
      var cohort = response.data;
      if (cohort) {
        // Search results are member list of the cohort
        $scope.search.results.totalCount = cohort.totalMemberCount;
        $scope.search.results.rows = cohort.members;
      } else {
        $scope.error = {message: 'Cohort not found'};
      }
      return cohort;
    };

    var refreshCohortView = function(code, callback) {
      // Pagination is not used on teams because the member count is always reasonable.
      $scope.pagination.enabled = !isNaN(code);
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 0;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;
      cohortFactory.getCohort(code, $scope.orderBy.selected, offset, limit).then(
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

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {String[]}    teamCodes          Array of predefined team codes
     * @return {void}
     */
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
        refreshCohortView($scope.cohort.code || $scope.cohort.id, angular.noop);
      } else {
        var teamCodes = _.map($scope.search.selected.teams, 'code');
        $scope.pagination.enabled = true;
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

    var loadScatterplot = function(response) {
      // Plot the cohort
      var partitionedMembers = _.partition(response.data.members, function(member) {
        return _.isFinite(_.get(member, 'analytics.pageViews'));
      });
      var goToUserPage = function(uid) {
        $state.go('user', {uid: uid});
      };
      // Render graph
      $scope.matrix = {
        membersWithData: partitionedMembers[0],
        membersWithoutData: partitionedMembers[1]
      };
      cohortService.displayCohort($scope.matrix.membersWithData, goToUserPage);
    };

    /**
     * List view is paginated but Matrix view must show all users. Lazy load the Matrix tab.
     *
     * @param  {String}    tabName          Name of tab clicked by user
     * @return {void}
     */
    $scope.onTab = function(tabName) {
      $scope.selectedTab = tabName;

      // Lazy load matrix data
      if (tabName === 'matrix' && !$scope.matrix) {
        $scope.isMatrixLoading = true;
        // Functions
        var handleError = function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        };
        var done = function() {
          $scope.isMatrixLoading = false;
        };

        if ($scope.cohort) {
          var code = $scope.cohort.code || $scope.cohort.id;
          cohortFactory.getCohort(code, null, 0, $scope.pagination.noLimit).then(loadScatterplot).catch(handleError).then(done);
        } else {
          cohortFactory.getTeamsMembers(teamCodes, null, 0, $scope.pagination.noLimit).then(loadScatterplot).catch(handleError).then(done);
        }
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

    var init = function(cohortCode) {
      var code = cohortCode || $stateParams.code;

      cohortFactory.getTeams().then(function(teams) {
        // Populate search form
        $scope.search.options.teams = teams.data;

        // if code is "0" then we offer a blank slate, the first step in creating a new cohort.
        if ($stateParams.code === '0') {
          $scope.isLoading = false;
        } else {
          $scope.selectedTab = 'list';

          refreshCohortView(code, function(cohort) {
            if (cohort) {
              // A team will have a single team code and a saved cohort might have multiple.
              var teamCodes = cohort.code ? [ cohort.code ] : _.map(cohort.teams, 'code');
              refreshSearchForm(teamCodes);
            }
            // Done!
            $scope.isLoading = false;
          });
        }
      });
    };

    $rootScope.$on('cohortCreated', function(event, data) {
      $scope.pagination.enabled = true;
      $scope.pagination.currentPage = 0;

      init(data.cohort.id);
    });

    authService.authWrap(init)();

  });
}(window.angular));
