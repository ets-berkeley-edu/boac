(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(
    authService,
    boxplotService,
    cohortFactory,
    cohortService,
    googleAnalyticsService,
    studentFactory,
    utilService,
    $anchorScroll,
    $base64,
    $location,
    $rootScope,
    $scope,
    $state,
    $timeout
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
      defaultTab: 'list',
      selected: 'list'
    };

    $scope.cohort = {
      code: null,
      members: [],
      totalMemberCount: null
    };

    $scope.search = {
      count: {
        gpaRanges: 0,
        teamGroups: 0,
        levels: 0,
        majors: 0,
        unitRanges: 0
      },
      dropdown: defaultDropdownState(),
      filterByUnitsFeatureEnabled: false,
      options: {}
    };

    $scope.orderBy = {
      options: [
        {value: 'first_name', label: 'First Name'},
        {value: 'last_name', label: 'Last Name'},
        {value: 'group_name', label: 'Team'},
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
     * Update cohort in scope; insure a valid cohort.code.
     *
     * @param  {Object}    data        Response data with cohort/search results
     * @return {void}
     */
    var updateCohort = function(data) {
      $scope.cohort = data;
      $scope.cohort.code = $scope.cohort.code || 'search';
    };

    /**
     * Use selected filter options to query students API.
     *
     * TODO: The search-by-unit-ranges feature is disabled and likely to change
     * var unitRangesEligibility = cohortService.getSelected(opts.unitRangesEligibility, 'value');
     * var unitRangesPacing = cohortService.getSelected(opts.unitRangesPacing, 'value');
     *
     * @param  {String}      orderBy                     Requested sort order
     * @param  {Number}      offset                      As used in SQL query
     * @param  {Number}      limit                       As used in SQL query
     * @param  {Number}      updateBrowserLocation       If true, we will update search criteria in browser location URL
     * @return {List}                                    Backend API results
     */
    var getStudents = function(orderBy, offset, limit, updateBrowserLocation) {
      var opts = $scope.search.options;
      var gpaRanges = cohortService.getSelected(opts.gpaRanges, 'value');
      var groupCodes = cohortService.getSelected(opts.teamGroups, 'groupCode');
      var levels = cohortService.getSelected(opts.levels, 'name');
      var majors = cohortService.getSelected(opts.majors, 'name');
      if (updateBrowserLocation) {
        $location.search('c', 'search');
        $location.search('g', gpaRanges);
        $location.search('t', groupCodes);
        $location.search('l', levels);
        $location.search('m', majors);
      }
      return studentFactory.getStudents(gpaRanges, groupCodes, levels, majors, [], [], orderBy, offset, limit);
    };

    /**
     * Call factory method per cohort.code or search criteria.
     *
     * @param  {String}    orderBy     Informs db query
     * @param  {Number}    offset      Per pagination
     * @param  {Number}    limit       Per pagination
     * @return {Promise}               Factory function
     */
    var getCohort = function(orderBy, offset, limit) {
      var promise;
      if ($scope.cohort.code === 'search') {
        promise = getStudents(orderBy, offset, limit, true);
      } else if ($scope.cohort.code === 'intensive') {
        promise = cohortFactory.getIntensiveCohort(orderBy, offset, limit);
      } else if (isNaN($scope.cohort.code)) {
        promise = cohortFactory.getTeam($scope.cohort.code, orderBy, offset, limit);
      } else {
        promise = cohortFactory.getCohort($scope.cohort.code, orderBy, offset, limit);
      }
      return promise;
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
              var dataset = _.get(canvasSite, 'analytics.pageViews');
              // If the course site has not yet been viewed, then there is nothing to plot.
              if (dataset && _.get(dataset, 'courseDeciles')) {
                boxplotService.drawBoxplotCohort(elementId, dataset);
              }
            });
          });
        });
      });
    };

    /**
     * Invoke API to get cohort, team or intensive.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var listViewRefresh = function(callback) {
      // Pagination is not used on teams because the member count is always reasonable.
      $scope.pagination.enabled = _.includes(['search', 'intensive'], $scope.cohort.code) || !isNaN($scope.cohort.code);
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 0;
      var orderBy = $scope.orderBy.selected;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;

      $scope.isLoading = true;
      getCohort(orderBy, offset, limit).then(function(response) {
        updateCohort(response.data);
        drawBoxplots();
        return callback();
      }).catch(function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        return callback(null);
      });
    };

    /**
     * Request parameters (query args) can will set 'selected=true' in cohort search filters. This feature supports
     * the 'Return to results' link offered on student profile page.
     *
     * @param  {String}      filterName      Represents a dropdown (ie, search filter) used to search by teamGroup, etc.
     * @param  {Function}    key             Used to compare filter options to incoming request parameters (ie, selectedValues).
     * @param  {Function}    selectedValues  These values represent request parameters (e.g., list of majors)
     * @return {void}
     */
    var preset = function(filterName, key, selectedValues) {
      if (!_.isEmpty(selectedValues)) {
        _.each($scope.search.options[filterName], function(option) {
          if (_.includes(selectedValues, option[key])) {
            option.selected = true;
            $scope.search.count[filterName] += 1;
          }
        });
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var initFilters = function(callback) {
      if ($scope.cohort.filterCriteria || $scope.cohort.teamGroups) {
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
        $scope.search.count.teamGroups = selectedGroupCodes.length;
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
      }
      // Ready for the world!
      return callback();
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
        return _.isFinite(_.get(member, 'analytics.pageViews.percentile')) &&
          _.isFinite(_.get(member, yAxisMeasure + '.percentile'));
      });
      // Pass along a subset of students that have useful data.
      cohortService.drawScatterplot(partitions[0], yAxisMeasure, function(uid) {
        var encodedAbsUrl = $base64.encode($location.absUrl());
        $state.go('user', {uid: uid, r: encodedAbsUrl});
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
      getCohort(null, 0, $scope.pagination.noLimit).then(function(response) {
        updateCohort(response.data);
        scatterplotRefresh();
        return callback();
      }).catch(function(err) {
        $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        return callback();
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
          $scope.isLoading = false;
        });
      } else {
        $scope.pagination.enabled = true;

        var handleSuccess = function(response) {
          updateCohort(response.data);
          drawBoxplots();
        };

        var handleError = function(err) {
          $scope.error = err ? {message: err.status + ': ' + err.statusText} : true;
        };
        var page = $scope.pagination.currentPage;
        var offset = page === 0 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

        // Perform the query
        $scope.isLoading = true;
        getStudents($scope.orderBy.selected, offset, $scope.pagination.itemsPerPage, true).then(handleSuccess, handleError).then(function() {
          $scope.isLoading = false;
        });
      }
    };

    /**
     * Invoked when state is initializing. Preset filters and search criteria prior to cohort API call.
     *
     * @param  {Object}    args     See $location.search()
     * @return {void}
     */
    var presetSearchFilters = function(args) {
      if ($scope.cohort.code === 'search' && !_.isEmpty(args)) {
        preset('gpaRanges', 'value', args.g);
        preset('teamGroups', 'groupCode', args.t);
        preset('levels', 'name', args.l);
        preset('majors', 'name', args.m);
      }
      if (args.o && _.find($scope.orderBy.options, ['value', args.o])) {
        $scope.orderBy.selected = args.o;
      }
      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
      }
      if (args.v && _.includes($scope.tabs.all, args.v)) {
        $scope.tabs.selected = args.v;
      }
      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
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
      $location.search('v', $scope.tabs.selected);
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
      $scope.isCreateCohortMode = false;
      $scope.search.dropdown = defaultDropdownState();
      // Refresh search results
      $scope.cohort.code = 'search';
      $scope.pagination.currentPage = 0;
      $location.search('c', $scope.cohort.code);
      $location.search('p', $scope.pagination.currentPage);
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
        $location.search('o', $scope.orderBy.selected);
        $scope.pagination.currentPage = 0;
        nextPage();
      }
    });

    $scope.$watch('pagination.currentPage', function() {
      if (!$scope.isLoading) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    $scope.studentProfile = function(uid) {
      var encodedAbsUrl = $base64.encode($location.absUrl());
      $location.path('/student/' + uid).search({r: encodedAbsUrl});
    };

    $scope.toggleFilter = function(event) {
      // Known issue: https://github.com/angular-ui/bootstrap/issues/6038
      if (event) {
        event.stopPropagation();
      }
    };

    /**
     * Initialize page view.
     *
     * @return {void}
     */
    var init = authService.authWrap(function() {
      var args = _.clone($location.search());
      // Create-new-cohort mode if code='new'. Search-mode (ie, unsaved cohort) if code='search'.
      var code = $scope.cohort.code || args.c || 'search';
      $scope.cohort.code = isNaN(code) ? code : parseInt(code, 10);
      $scope.isCreateCohortMode = $scope.cohort.code === 'new';

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
          // Filter options to 'selected' per request args
          presetSearchFilters(args);

          if ($scope.isCreateCohortMode) {
            initFilters(function() {
              $scope.isLoading = false;
            });
          } else {
            var render = $scope.tabs.selected === 'list' ? listViewRefresh : matrixViewRefresh;
            render(function() {
              initFilters(function() {
                $scope.isLoading = false;
                if (args.a) {
                  $timeout(function() {
                    // Scroll to anchor if returning from student profile page
                    $scope.anchor = args.a;
                    $location.search('a', null).replace();
                    $anchorScroll.yOffset = 50;
                    $anchorScroll(args.a);
                  });
                }
                // Track view event
                if (isNaN($scope.cohort.code)) {
                  googleAnalyticsService.track('team', 'view', $scope.cohort.code + ': ' + $scope.cohort.name);
                } else {
                  googleAnalyticsService.track('cohort', 'view', $scope.cohort.name, $scope.cohort.code);
                }
              });
            });
          }
        });
      });
    });

    /**
     * Reload page with newly created cohort.
     */
    $rootScope.$on('cohortCreated', function(event, data) {
      $scope.isCreateCohortMode = false;
      var id = data.cohort.id;
      $scope.cohort.code = id;
      $scope.cohort.name = data.cohort.name;
      $location.url($location.path());
      $location.search('c', id);
    });

    $scope.$$postDigest(init);

  });
}(window.angular));
