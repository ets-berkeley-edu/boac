(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(
    authService,
    boxplotService,
    cohortFactory,
    cohortService,
    googleAnalyticsService,
    studentFactory,
    $location,
    $rootScope,
    $scope,
    $state,
    $stateParams
  ) {

    $scope.isLoading = true;
    $scope.selectedTab = 'list';
    $scope.isCreateCohortMode = false;

    var defaultDropdownState = function() {
      return {
        gpaRangesOpen: false,
        levelsOpen: false,
        majorsOpen: false,
        groupCodesOpen: false,
        unitsOpen: false
      };
    };

    $scope.search = {
      count: {
        gpaRanges: 0,
        groupCodes: 0,
        levels: 0,
        majors: 0,
        unitRangesEligibility: 0,
        unitRangesPacing: 0
      },
      dropdown: defaultDropdownState(),
      options: {},
      results: {
        rows: null,
        totalCount: null
      }
    };

    $scope.orderBy = {
      options: [{value: 'first_name', label: 'First Name'}, {value: 'last_name', label: 'Last Name'}],
      selected: 'first_name'
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
      var isTeam = isNaN(code);
      $scope.pagination.enabled = !isTeam;
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 0;
      var orderBy = $scope.orderBy.selected;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;

      var handleSuccess = function(response) {
        return callback(parseCohortFeed(response));
      };
      var handleError = function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        return callback(null);
      };
      $scope.isLoading = true;
      if (code === 'intensive') {
        cohortFactory.getIntensiveCohort(orderBy, offset, limit).then(handleSuccess, handleError);
      } else if (isTeam) {
        cohortFactory.getTeam(code, orderBy).then(handleSuccess, handleError);
      } else {
        cohortFactory.getCohort(code, orderBy, offset, limit).then(handleSuccess, handleError);
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {String[]}    cohort      Null if we are in create-cohort-mode
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var initFilters = function(cohort, callback) {
      cohortFactory.getAllTeamGroups().then(function(response) {
        $scope.search.options = {
          levels: studentFactory.getStudentLevels(),
          teamGroups: response.data
        };
        // Team group codes
        var selectedGroupCodes = [];
        if (cohort) {
          if (cohort.teamGroups) {
            selectedGroupCodes = _.map(cohort.teamGroups, 'groupCode');
          } else {
            selectedGroupCodes = _.get(cohort, 'filterCriteria.groupCodes', []);
          }
        }
        $scope.search.count.groupCodes = selectedGroupCodes.length;
        _.map($scope.search.options.teamGroups, function(teamGroup) {
          teamGroup.selected = _.includes(selectedGroupCodes, teamGroup.groupCode);
        });
        // Class levels
        var selectedLevels = _.get(cohort, 'filterCriteria.levels', []);
        $scope.search.count.levels = selectedLevels.length;
        _.map($scope.search.options.levels, function(level) {
          level.selected = _.includes(selectedLevels, level.name);
        });
        return callback();
      });
    };

    var getSelectedGroupCodes = function() {
      var groupCodes = _.filter($scope.search.options.teamGroups, 'selected');
      return _.map(groupCodes, 'groupCode');
    };

    var scatterplotRefresh = function(response) {
      // Plot the cohort
      var yAxisMeasure = $scope.yAxisMeasure = $location.search().yAxis || 'analytics.assignmentsOnTime';
      var partitionedMembers = _.partition(response.data.members, function(member) {
        return _.isFinite(_.get(member, 'analytics.pageViews')) && _.isFinite(_.get(member, yAxisMeasure));
      });
      var goToUserPage = function(uid) {
        $state.go('user', {uid: uid});
      };

      // Render graph
      $scope.matrix = {
        membersWithData: partitionedMembers[0],
        membersWithoutData: partitionedMembers[1]
      };
      cohortService.drawScatterplot($scope.matrix.membersWithData, goToUserPage, yAxisMeasure);
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
      var noLimit = $scope.pagination.noLimit;
      if ($scope.cohort) {
        if ($scope.cohort.code) {
          if ($scope.cohort.code === 'intensive') {
            cohortFactory.getIntensiveCohort(null, 0, noLimit).then(scatterplotRefresh).catch(handleError).then(done);
          } else {
            cohortFactory.getTeam($scope.cohort.code, null, 0, noLimit).then(scatterplotRefresh).catch(handleError).then(done);
          }
        } else {
          cohortFactory.getCohort($scope.cohort.id, null, 0, noLimit).then(scatterplotRefresh).catch(handleError).then(done);
        }
      } else {
        studentFactory.getStudents(getSelectedGroupCodes(), null, 0, noLimit).then(scatterplotRefresh).catch(handleError).then(done);
      }
    };

    var listViewRefresh = function() {
      if ($scope.cohort) {
        refreshCohortView($scope.cohort.code || $scope.cohort.id, function(cohort) {
          $scope.cohort = cohort;
          $scope.isLoading = false;
        });
      } else {
        $scope.pagination.enabled = true;

        var handleError = function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        };
        var page = $scope.pagination.currentPage;
        var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

        // Perform the query
        $scope.isLoading = true;
        studentFactory.getStudents(getSelectedGroupCodes(), $scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(parseCohortFeed, handleError).then(function() {
          $scope.isLoading = false;
        });
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {String}    type     Dropdown name
     * @param  {Number}    option   Has been selected or deselected
     * @return {void}
     */
    $scope.updateSelected = function(type, option) {
      var delta = option.selected ? 1 : -1;
      var existingValue = _.get($scope.search.count, type, 0);
      _.set($scope.search.count, type, existingValue + delta);
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
      $scope.search.dropdown = defaultDropdownState();
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

    $scope.drawActivityBoxplot = function(student, courseSite) {
      var elementId = 'boxplot-' + courseSite.canvasCourseId + '-' + student.uid + '-pageviews';
      boxplotService.drawBoxplotCohort(elementId, courseSite.analytics.pageViews);
    };

    var init = function(cohortCode) {
      // if code is "0" then we offer a blank slate, the first step in creating a new cohort.
      var code = cohortCode || $stateParams.code;
      $scope.isCreateCohortMode = code === '0';
      if ($scope.isCreateCohortMode) {
        initFilters(null, function() {
          $scope.isLoading = false;
        });
      } else {
        refreshCohortView(code, function(cohort) {
          initFilters(cohort, function() {
            $scope.cohort = cohort;
            $scope.isLoading = false;
            if (cohort) {
              // Track view event
              if (cohort.code) {
                googleAnalyticsService.track('team', 'view', cohort.code + ': ' + cohort.name);
              } else {
                googleAnalyticsService.track('cohort', 'view', cohort.label, cohort.id);
              }
            }
          });
        });
      }
    };

    $rootScope.$on('cohortCreated', function(event, data) {
      $scope.search.dropdown = defaultDropdownState();
      $scope.pagination.enabled = true;
      $scope.pagination.currentPage = 0;
      init(data.cohort.id);
    });

    authService.authWrap(init)();

  });
}(window.angular));
