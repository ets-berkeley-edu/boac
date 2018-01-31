(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(
    boxplotService,
    cohortFactory,
    cohortService,
    googleAnalyticsService,
    studentFactory,
    utilService,
    watchlistFactory,
    $anchorScroll,
    $base64,
    $location,
    $rootScope,
    $scope,
    $state,
    $timeout
  ) {

    /**
     * Control show/hide of dropdowns: true -> show, false -> hide
     *
     * @return {Object}                Each filter dropdown (unique key) has state (true/false)
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
      currentPage: 1,
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
      var unitRanges = cohortService.getSelected(opts.unitRanges, 'value');
      if (updateBrowserLocation) {
        $location.search('c', 'search');
        $location.search('g', gpaRanges);
        $location.search('t', groupCodes);
        $location.search('l', levels);
        $location.search('m', majors);
        $location.search('u', unitRanges);
      }
      return studentFactory.getStudents(gpaRanges, groupCodes, levels, majors, unitRanges, orderBy, offset, limit);
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

    var isPaginationEnabled = function() {
      return _.includes(['search', 'intensive'], $scope.cohort.code) || !isNaN($scope.cohort.code);
    };

    /**
     * Invoke API to get cohort, team or intensive.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var listViewRefresh = function(callback) {
      // Pagination is not used on teams because the member count is always reasonable.
      $scope.pagination.enabled = isPaginationEnabled();
      var page = $scope.pagination.enabled ? $scope.pagination.currentPage : 1;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = page === 0 ? 0 : (page - 1) * limit;

      $scope.isLoading = true;
      getCohort($scope.orderBy.selected, offset, limit).then(function(response) {
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
          if (option && _.includes(selectedValues, option[key])) {
            option.selected = true;
            $scope.search.count[filterName] += 1;
          }
        });
      }
    };

    /**
     * @param  {Array}     allOptions     All options of dropdown
     * @param  {Function}  isSelected     Determines value of 'selected' property
     * @return {void}
     */
    var setSelected = function(allOptions, isSelected) {
      _.each(allOptions, function(option) {
        if (option) {
          option.selected = isSelected(option);
        }
      });
    };

    /**
     * @param  {String}    menuName     For example, 'gpaRanges'
     * @param  {Object}    option       Has been selected or deselected
     * @return {void}
     */
    var onClickOption = function(menuName, option) {
      var delta = option.selected ? 1 : -1;
      var existingValue = _.get($scope.search.count, menuName, 0);
      _.set($scope.search.count, menuName, existingValue + delta);
    };

    /**
     * Ordinarily, the value of 'selected' (per dropdown menu option) is managed by uib-dropdown-toggle in the
     * template. However, we sometimes want to alter option 'selected' behind the scenes.
     *
     * @param  {String}    menuName         For example, 'majors'
     * @param  {String}    optionName       For example, the option group 'Declared'
     * @param  {Boolean}   value            The value used to update 'selected' property
     * @return {void}
     */
    var manualSetSelected = function(menuName, optionName, value) {
      var allMenuOptions = _.get($scope.search.options, menuName);
      var match = _.find(allMenuOptions, {name: optionName});
      if (match && !!match.selected !== !!value) {
        match.selected = value;
        onClickOption(menuName, match);
      }
    };

    /**
     * @param  {String}    menuName      For example, 'majors'
     * @param  {Object}    optionGroup   Menu represents a group of options (see option-group definition)
     * @return {void}
     */
    var onClickOptionGroup = function(menuName, optionGroup) {
      if (menuName === 'majors') {
        if (optionGroup.selected) {
          if (optionGroup.name === 'Declared') {
            // If user selects "Declared" then all other checkboxes are deselected
            $scope.search.count.majors = 1;
            setSelected($scope.search.options.majors, function(major) {
              return major.name === optionGroup.name;
            });
          } else if (optionGroup.name === 'Undeclared') {
            // If user selects "Undeclared" then "Declared" is deselected
            manualSetSelected(menuName, 'Declared', false);
            onClickOption(menuName, optionGroup);
          }
        } else {
          onClickOption(menuName, optionGroup);
        }
      }
    };

    /**
     * @param  {String}    menuName     Always 'majors'
     * @param  {Object}    option       Has been selected or deselected
     * @return {void}
     */
    var onClickSpecificMajor = function(menuName, option) {
      manualSetSelected('majors', 'Declared', false);
      onClickOption(menuName, option);
    };

    var getCohortCriteria = function(property) {
      return $scope.cohort.filterCriteria ? _.get($scope.cohort, 'filterCriteria.' + property, []) : null;
    };

    /**
     * @param  {String}     menuName            For example, 'gpaRanges' or 'majors'
     * @param  {String}     valueRef            Key to use when looking up menu option values
     * @param  {Object}     selectedSet         Pre-selected cohort filter criteria per search or db record
     * @param  {Function}   onClickFunction     The function we add to object will be invoked onClick.
     * @return {void}
     */
    var initFilter = function(menuName, valueRef, selectedSet, onClickFunction) {
      if (selectedSet !== null) {
        $scope.search.count[menuName] = selectedSet.length;
        _.map($scope.search.options[menuName], function(option) {
          if (option) {
            option.selected = _.includes(selectedSet, option[valueRef]);
          }
        });
      }
      if (onClickFunction) {
        _.map($scope.search.options[menuName], function(option) { option.onClick = onClickFunction; });
      }
    };

    /**
     * The search form must reflect the team codes of the saved cohort.
     *
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var initFilters = function(callback) {
      // GPA ranges
      initFilter('gpaRanges', 'value', getCohortCriteria('gpaRanges'), onClickOption);
      // Teams (if we receive a teamCode then init filter with groupCodes of that team)
      var selectedCodes = $scope.cohort.teamGroups ? _.map($scope.cohort.teamGroups, 'groupCode') : getCohortCriteria('groupCodes');
      initFilter('teamGroups', 'groupCode', selectedCodes, onClickOption);
      // Levels
      initFilter('levels', 'name', getCohortCriteria('levels'), onClickOption);
      // Majors (the 'Declared' and 'Undeclared' options are special)
      _.map($scope.search.options.majors, function(option) {
        if (option) {
          option.onClick = option.onClick || onClickSpecificMajor;
        }
      });
      initFilter('majors', 'name', getCohortCriteria('majors'));
      // Units
      initFilter('unitRanges', 'value', getCohortCriteria('unitRanges'), onClickOption);
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
        var absUrl = $location.absUrl();
        $location.state(absUrl);
        var encodedAbsUrl = encodeURIComponent($base64.encode(absUrl));
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
        var offset = page < 2 ? 0 : (page - 1) * $scope.pagination.itemsPerPage;

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
        preset('unitRanges', 'value', args.u);
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
        // Restore pagination; fortunately, 'currentPage' persists.
        $scope.pagination.enabled = isPaginationEnabled();
        if ($scope.pagination.enabled && $scope.pagination.currentPage > 1 && $scope.cohort.members.length > 50) {
          var start = ($scope.pagination.currentPage - 1) * 50;
          $scope.cohort.members = _.slice($scope.cohort.members, start, start + 50);
        }
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
      $scope.pagination.currentPage = 1;
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
        $scope.pagination.currentPage = 1;
        nextPage();
      }
    });

    $scope.$watch('pagination.currentPage', function() {
      if (!$scope.isLoading) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    $scope.studentProfile = function(uid) {
      var encodedAbsUrl = encodeURIComponent($base64.encode($location.absUrl()));
      $location.path('/student/' + uid).search({r: encodedAbsUrl});
    };

    $scope.toggleFilter = function(event) {
      // Known issue: https://github.com/angular-ui/bootstrap/issues/6038
      if (event) {
        event.stopPropagation();
      }
    };

    var getMajors = function(callback) {
      studentFactory.getRelevantMajors().then(function(majorsResponse) {
        var majors = _.map(majorsResponse.data, function(name) {
          return {name: name};
        });
        majors.unshift(
          {
            name: 'Declared',
            onClick: onClickOptionGroup
          },
          {
            name: 'Undeclared',
            onClick: onClickOptionGroup
          },
          null
        );
        return callback(majors);
      });
    };

    /**
     * Initialize page view.
     *
     * @return {void}
     */
    var init = function() {
      var args = _.clone($location.search());
      // Create-new-cohort mode if code='new'. Search-mode (ie, unsaved cohort) if code='search'.
      var code = $scope.cohort.code || args.c || 'search';
      $scope.cohort.code = isNaN(code) ? code : parseInt(code, 10);
      $scope.isCreateCohortMode = $scope.cohort.code === 'new';

      cohortFactory.getAllTeamGroups().then(function(teamsResponse) {
        var teamGroups = teamsResponse.data;

        getMajors(function(majors) {
          $scope.search.options = {
            gpaRanges: studentFactory.getGpaRanges(),
            levels: studentFactory.getStudentLevels(),
            majors: majors,
            teamGroups: teamGroups,
            unitRanges: studentFactory.getUnitRanges()
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
                watchlistFactory.getMyWatchlist().then(function(response) {
                  $scope.myWatchlist = response.data;
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
            });
          }
        });
      });
    };

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
