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

    /**
     * Used to collapse all dropdown menus (e.g., if user clicks 'Search').
     *
     * @return {Object}      One entry per dropdown/filter.
     */
    var defaultDropdownState = function() {
      return {
        gpaRangesOpen: false,
        levelsOpen: false,
        majorsOpen: false,
        groupCodesOpen: false,
        unitRangesOpen: false
      };
    };

    $scope.isLoading = true;
    $scope.isCreateCohortMode = false;

    $scope.tabs = {
      all: ['list', 'matrix'],
      selected: null
    };

    $scope.cohort = {
      code: null,
      members: [],
      totalMemberCount: null
    };

    $scope.search = {
      count: {
        gpaRanges: 0,
        groupCodes: 0,
        levels: 0,
        majors: 0,
        unitRanges: 0
      },
      dropdown: defaultDropdownState(),
      options: {}
    };

    $scope.orderBy = {
      options: [
        {value: 'first_name', label: 'First Name'},
        {value: 'last_name', label: 'Last Name'},
        {value: 'group_code', label: 'Team'},
        {value: 'gpa', label: 'GPA'},
        {value: 'level', label: 'Level'},
        {value: 'major', label: 'Major'},
        {value: 'units', label: 'Units'}
      ],
      selected: 'first_name'
    };

    // More info: https://angular-ui.github.io/bootstrap/
    $scope.pagination = {
      enabled: true,
      currentPage: 0,
      itemsPerPage: 50,
      noLimit: Number.MAX_SAFE_INTEGER
    };

    /**
     * Extract query args as soon as $location is available.
     */
    $scope.$watch('$location', function() {
      var args = $location.search();
      $scope.tabs.selected = _.includes($scope.tabs.all, args.t) ? args.t : 'list';
    });

    /**
     * Invoke API to get cohort, team or intensive.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var listViewRefresh = function(callback) {
      // Pagination is not used on teams because the member count is always reasonable.
      var isTeam = isNaN($scope.cohort.code);
      $scope.pagination.enabled = !isTeam;
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 0;
      var orderBy = $scope.orderBy.selected;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;

      var handleSuccess = function(response) {
        $scope.cohort = response.data;
        return callback();
      };
      var handleError = function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        return callback(null);
      };
      $scope.isLoading = true;
      if ($scope.cohort.code === 'intensive') {
        cohortFactory.getIntensiveCohort(orderBy, offset, limit).then(handleSuccess, handleError);
      } else if (isTeam) {
        cohortFactory.getTeam($scope.cohort.code, orderBy).then(handleSuccess, handleError);
      } else {
        cohortFactory.getCohort($scope.cohort.code, orderBy, offset, limit).then(handleSuccess, handleError);
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var initFilters = function(callback) {
      cohortFactory.getAllTeamGroups().then(function(teamsResponse) {
        var teamGroups = teamsResponse.data;

        studentFactory.getRelevantMajors().then(function(response) {
          var majors = _.map(response.data, function(name) {
            return {name: name};
          });
          $scope.search.options = {
            gpaRanges: studentFactory.getGpaRanges(),
            levels: studentFactory.getStudentLevels(),
            majors: majors,
            teamGroups: teamGroups,
            unitRangesEligibility: studentFactory.getUnitRangesEligibility(),
            unitRangesPacing: studentFactory.getUnitRangesPacing()
          };
          // GPA ranges
          var selectedGpaRanges = _.get($scope.cohort, 'filterCriteria.gpaRanges', []);
          $scope.search.count.gpaRanges = selectedGpaRanges.length;
          _.map($scope.search.options.gpaRanges, function(gpaRange) {
            gpaRange.selected = _.includes(selectedGpaRanges, gpaRange.value);
          });
          // If we hit the cohort view with a team code then we populate filter with the team's group codes.
          var selectedGroupCodes = [];
          if ($scope.cohort.teamGroups) {
            selectedGroupCodes = _.map($scope.cohort.teamGroups, 'groupCode');
          } else {
            selectedGroupCodes = _.get($scope.cohort, 'filterCriteria.groupCodes', []);
          }
          $scope.search.count.groupCodes = selectedGroupCodes.length;
          _.map($scope.search.options.teamGroups, function(teamGroup) {
            teamGroup.selected = _.includes(selectedGroupCodes, teamGroup.groupCode);
          });
          // Class levels
          var selectedLevels = _.get($scope.cohort, 'filterCriteria.levels', []);
          $scope.search.count.levels = selectedLevels.length;
          _.map($scope.search.options.levels, function(level) {
            level.selected = _.includes(selectedLevels, level.name);
          });
          // Majors
          var selectedMajors = _.get($scope.cohort, 'filterCriteria.majors', []);
          $scope.search.count.majors = selectedMajors.length;
          _.map($scope.search.options.majors, function(major) {
            major.selected = _.includes(selectedMajors, major.name);
          });
          // Units, eligibility
          var selectedUnitRangesE = _.get($scope.cohort, 'filterCriteria.unitRangesEligibility', []);
          _.map($scope.search.options.unitRangesEligibility, function(unitRange) {
            unitRange.selected = _.includes(selectedUnitRangesE, unitRange.value);
          });
          // Units, pacing
          var selectedUnitRangesP = _.get($scope.cohort, 'filterCriteria.unitRangesPacing', []);
          _.map($scope.search.options.unitRangesPacing, function(unitRange) {
            unitRange.selected = _.includes(selectedUnitRangesP, unitRange.value);
          });
          $scope.search.count.unitRanges = selectedUnitRangesE.length + selectedUnitRangesP.length;
          // Ready for the world!
          return callback();
        });
      });
    };

    /**
     * Use selected filter options to query students API.
     *
     * @param  {String}      orderBy     Requested sort order
     * @param  {Number}      offset      As used in SQL query
     * @param  {Number}      limit       As used in SQL query
     * @return {List}                    Backend API results
     */
    var getStudents = function(orderBy, offset, limit) {
      var opts = $scope.search.options;
      return studentFactory.getStudents(
        cohortService.getSelected(opts.gpaRanges, 'value'),
        cohortService.getSelected(opts.teamGroups, 'groupCode'),
        cohortService.getSelected(opts.levels, 'name'),
        cohortService.getSelected(opts.majors, 'name'),
        cohortService.getSelected(opts.unitRangesEligibility, 'value'),
        cohortService.getSelected(opts.unitRangesPacing, 'value'),
        orderBy,
        offset,
        limit);
    };

    /**
     * Draw scatterplot graph.
     *
     * @param  {Object}      response       Data from backend API
     * @return {void}
     */
    var scatterplotRefresh = function() {
      // Plot the cohort
      var yAxisMeasure = $scope.yAxisMeasure = $location.search().yAxis || 'analytics.courseCurrentScore';
      var partitions = _.partition($scope.cohort.members, function(member) {
        return _.isFinite(_.get(member, 'analytics.pageViews')) && _.isFinite(_.get(member, yAxisMeasure));
      });
      // Pass along a subset of students that have useful data.
      cohortService.drawScatterplot(partitions[0], yAxisMeasure, function(uid) {
        $state.go('user', {uid: uid});
      });
      // List of students-without-data is rendered below the scatterplot.
      $scope.studentsWithoutData = partitions[1];
    };

    /**
     * Get ALL students of the cohort then render the scatterplot graph.
     *
     * @param  {Function}    callback      Standard callback function
     * @return {void}
     */
    var matrixViewRefresh = function(callback) {
      $scope.isLoading = true;
      var noLimit = $scope.pagination.noLimit;
      var handleError = function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        return callback();
      };
      var handleSuccess = function(response) {
        $scope.cohort = response.data;
        scatterplotRefresh();
        return callback();
      };
      if (_.isEmpty($scope.cohort.code)) {
        getStudents(null, 0, noLimit).then(handleSuccess).catch(handleError).then(callback);
      } else if ($scope.cohort.code === 'intensive') {
        cohortFactory.getIntensiveCohort(null, 0, noLimit).then(handleSuccess).catch(handleError).then(callback);
      } else if (isNaN($scope.cohort.code)) {
        cohortFactory.getTeam($scope.cohort.code, null, 0, noLimit).then(handleSuccess).catch(handleError).then(callback);
      } else {
        cohortFactory.getCohort($scope.cohort.code, null, 0, noLimit).then(handleSuccess).catch(handleError).then(callback);
      }
    };

    /**
     * Draw boxplots for students in list view.
     *
     * @return {void}
     */
    var drawBoxplots = function() {
      // Wait until Angular has finished rendering elements within repeaters.
      $scope.$$postDigest(function() {
        _.each($scope.cohort.members, function(student) {
          _.each(_.get(student, 'currentTerm.enrollments'), function(enrollment) {
            _.each(_.get(enrollment, 'canvasSites'), function(canvasSite) {
              var elementId = 'boxplot-' + canvasSite.canvasCourseId + '-' + student.uid + '-pageviews';
              boxplotService.drawBoxplotCohort(elementId, _.get(canvasSite, 'analytics.pageViews'));
            });
          });
        });
      });
    };

    /**
     * Invoked when (1) user navigates to next/previous page or (2) search criteria changes.
     *
     * @return {void}
     */
    var nextPage = $scope.nextPage = function() {
      if ($scope.cohort.code) {
        listViewRefresh(function() {
          drawBoxplots();
          $scope.isLoading = false;
        });
      } else {
        $scope.pagination.enabled = true;

        var handleSuccess = function(response) {
          $scope.cohort = response.data;
          drawBoxplots();
        };

        var handleError = function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        };
        var page = $scope.pagination.currentPage;
        var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

        // Perform the query
        $scope.isLoading = true;
        getStudents($scope.orderBy.selected, offset, $scope.pagination.itemsPerPage).then(handleSuccess, handleError).then(function() {
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
      $scope.tabs.selected = tabName;
      // Lazy load matrix data
      if (tabName === 'matrix' && !$scope.matrix) {
        matrixViewRefresh(function() {
          $scope.isLoading = false;
        });
      } else if (tabName === 'list') {
        drawBoxplots();
      }
    };

    /**
     * Search per filter criteria.
     *
     * @return {void}
     */
    $scope.executeSearch = function() {
      $scope.search.dropdown = defaultDropdownState();
      // Refresh search results
      $scope.cohort.code = null;
      $scope.pagination.currentPage = 0;
      if ($scope.tabs.selected === 'list') {
        nextPage();
      } else {
        matrixViewRefresh(function() {
          $scope.isLoading = false;
        });
      }
    };

    $scope.$watch('orderBy.selected', function(value) {
      if (value && !$scope.isLoading) {
        $scope.pagination.currentPage = 0;
        nextPage();
      }
    });

    /**
     * Initialize page view.
     *
     * @return {void}
     */
    var init = function() {
      // if code is "0" then we offer a blank slate, the first step in creating a new cohort.
      $scope.cohort.code = $scope.cohort.code || $stateParams.code;
      $scope.isCreateCohortMode = $scope.cohort.code === '0';
      if ($scope.isCreateCohortMode) {
        initFilters(function() {
          $scope.isLoading = false;
        });
      } else {
        var render = $scope.tabs.selected === 'list' ? listViewRefresh : matrixViewRefresh;
        render(function() {
          initFilters(function() {
            drawBoxplots();
            $scope.isLoading = false;
            // Track view event
            if (isNaN($scope.cohort.code)) {
              googleAnalyticsService.track('team', 'view', $scope.cohort.code + ': ' + $scope.cohort.name);
            } else {
              googleAnalyticsService.track('cohort', 'view', $scope.cohort.name, $scope.cohort.code);
            }
          });
        });
      }
    };

    /**
     * Reload page with newly created cohort.
     */
    $rootScope.$on('cohortCreated', function(event, data) {
      $scope.search.dropdown = defaultDropdownState();
      $scope.pagination.enabled = true;
      $scope.pagination.currentPage = 0;
      $scope.cohort.code = data.cohort.id;
      $location.path('/cohort/' + $scope.cohort.code);
      init();
    });

    authService.authWrap(init)();

  });
}(window.angular));
