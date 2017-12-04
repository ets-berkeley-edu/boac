(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(authService, cohortFactory, cohortService, googleAnalyticsService, $rootScope, $scope, $state, $stateParams) {

    $scope.isLoading = true;
    $scope.selectedTab = 'list';
    $scope.isCreateCohortMode = false;

    $scope.search = {
      count: {
        selectedTeams: 0
      },
      dropdown: {
        teamsOpen: false
      },
      options: {
        teams: []
      },
      results: {
        rows: null,
        totalCount: null
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
      itemsPerPage: 50,
      noLimit: Number.MAX_SAFE_INTEGER
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
      $scope.isCreateCohortMode = false;
      return cohort;
    };

    var refreshCohortView = function(code, callback) {
      // Pagination is not used on teams because the member count is always reasonable.
      $scope.pagination.enabled = !isNaN(code);
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 0;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;

      $scope.isLoading = true;
      cohortFactory.getCohort(code, $scope.orderBy.selected, offset, limit).then(
        function(response) {
          $scope.cohort = parseCohortFeed(response);
          $scope.isLoading = false;
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
    var refreshTeamsFilter = function(teamCodes) {
      _.map($scope.search.options.teams, function(team) {
        team.selected = _.includes(teamCodes, team.code);
      });
    };

    var getSelectedTeamCodes = function() {
      var selectedTeams = _.filter($scope.search.options.teams, 'selected');
      return _.map(selectedTeams, 'code');
    };

    var scatterplotRefresh = function(response) {
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
      cohortService.drawScatterplot($scope.matrix.membersWithData, goToUserPage);
    };

    var matrixViewRefresh = function() {
      // In case of error
      var handleError = function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
      };
      // The done() function is always invoked
      $scope.isLoading = true;
      var done = function() {
        $scope.isLoading = false;
      };

      if ($scope.cohort) {
        var code = $scope.cohort.code || $scope.cohort.id;
        cohortFactory.getCohort(code, null, 0, $scope.pagination.noLimit).then(scatterplotRefresh).catch(handleError).then(done);
      } else {
        cohortFactory.getTeamsMembers(getSelectedTeamCodes(), null, 0, $scope.pagination.noLimit).then(scatterplotRefresh).catch(handleError).then(done);
      }
    };

    var listViewRefresh = function() {
      if ($scope.cohort) {
        refreshCohortView($scope.cohort.code || $scope.cohort.id, angular.noop);
      } else {
        $scope.pagination.enabled = true;

        var handleError = function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        };
        var page = $scope.pagination.currentPage;
        var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

        // Perform the query
        $scope.isLoading = true;
        cohortFactory.getTeamsMembers(getSelectedTeamCodes(), $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(parseCohortFeed, handleError).then(function() {
          $scope.isLoading = false;
        });
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {Number}    delta          Add this value to count of selected teams
     * @return {void}
     */
    $scope.updateSelectedTeamsCount = function(delta) {
      $scope.search.count.selectedTeams += delta;
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
        matrixViewRefresh();
      }
    };

    $scope.executeSearch = function() {
      // Close dropdown menu
      $scope.search.dropdown.teamsOpen = false;
      // Refresh search results
      $scope.cohort = null;
      $scope.pagination.currentPage = 0;
      if ($scope.selectedTab === 'list') {
        listViewRefresh();
      } else {
        matrixViewRefresh();
      }
    };

    $scope.nextPage = function() {
      listViewRefresh();
    };

    $scope.$watch('orderBy.selected', function(value) {
      if (value && !$scope.isLoading) {
        $scope.pagination.currentPage = 0;
        listViewRefresh();
      }
    });

    var init = function(cohortCode) {
      var code = cohortCode || $stateParams.code;

      cohortFactory.getTeams().then(function(teams) {
        $scope.search.options.teams = teams.data;
        // if code is "0" then we offer a blank slate, the first step in creating a new cohort.
        if (code === '0') {
          $scope.isCreateCohortMode = true;
          refreshTeamsFilter();
          $scope.isLoading = false;
        } else {
          refreshCohortView(code, function(cohort) {
            if (cohort) {
              // A team will have a single team code and a saved cohort might have multiple.
              var teamCodes = cohort.code ? [ cohort.code ] : _.map(cohort.teams, 'code');
              $scope.search.count.selectedTeams = teamCodes.length;
              refreshTeamsFilter(teamCodes);
              // Track view event
              if (cohort.code) {
                googleAnalyticsService.track('team', 'view', cohort.code + ': ' + cohort.name);
              } else {
                googleAnalyticsService.track('cohort', 'view', cohort.label, cohort.id);
              }
            }
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
