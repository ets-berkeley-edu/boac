/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

(function(angular) {

  'use strict';

  angular.module('boac').controller('FilteredCohortController', function(
    adminFactory,
    athleticsFactory,
    authService,
    config,
    filteredCohortFactory,
    googleAnalyticsService,
    page,
    studentFactory,
    studentSearchService,
    utilService,
    validationService,
    visualizationService,
    $location,
    $rootScope,
    $scope
  ) {

    var filters = {
      gpaRanges: 'g',
      groupCodes: 't',
      levels: 'l',
      majors: 'm',
      unitRanges: 'u'
    };

    /**
     * @return {Object}                Each dropdown has open or closed state
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

    page.loading(true);

    $scope.cohort = {
      code: null,
      students: [],
      totalStudentCount: null
    };
    $scope.currentEnrollmentTerm = config.currentEnrollmentTerm;
    $scope.demoMode = config.demoMode;
    $scope.isCreateCohortMode = false;
    $scope.isAscUser = authService.isAscUser();
    $scope.lastActivityDays = utilService.lastActivityDays;
    $scope.orderBy = studentSearchService.getSortByOptionsForSearch();
    $scope.pagination = {
      enabled: true,
      currentPage: 1,
      itemsPerPage: 50,
      noLimit: Number.MAX_SAFE_INTEGER
    };
    $scope.search = {
      checkboxes: {
        inactive: {
          checked: !!$location.search().inactive,
          label: 'Inactive',
          show: !!$location.search().inactive
        },
        intensive: {
          checked: !!$location.search().i,
          label: 'Intensive',
          show: !!$location.search().i
        },
        advisorLdapUid: {
          checked: !!$location.search().a,
          label: 'My Students',
          show: !!$location.search().a,
          value: $location.search().a
        }
      },
      count: {
        gpaRanges: 0,
        groupCodes: 0,
        levels: 0,
        majors: 0,
        unitRanges: 0
      },
      dropdown: defaultDropdownState(),
      options: {
        gpaRanges: null,
        groupCodes: null,
        levels: null,
        majors: null,
        unitRanges: null
      }
    };
    $scope.tab = 'list';

    $scope.exceedsMatrixThresholdMessage = utilService.exceedsMatrixThresholdMessage;

    var checkMatrixViewThreshold = function() {
      $scope.studentCountExceedsMatrixThreshold = utilService.exceedsMatrixThreshold(_.get($scope, 'cohort.totalStudentCount'));
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
      $rootScope.pageTitle = $scope.cohort.name || 'Filtered Cohort';
      var checkboxes = $scope.search.checkboxes;
      var customCohortName = null;
      if ($scope.isAscUser) {
        if (_.get($scope.cohort, 'filterCriteria.inIntensiveCohort') || checkboxes.intensive.checked) {
          checkboxes.show = checkboxes.checked = true;
          customCohortName = 'Intensive';
        } else if (_.get($scope.cohort, 'filterCriteria.isInactiveAsc') || checkboxes.inactive.checked) {
          checkboxes.inactive.show = checkboxes.inactive.checked = true;
          customCohortName = 'Inactive';
        }
      }
      if (customCohortName && $scope.cohort.code === 'search') {
        var useCustomCohortName = true;
        _.find($scope.search.options, function(menuItems) {
          _.each(menuItems, function(menuItem) {
            if (menuItem && menuItem.selected) {
              useCustomCohortName = false;
              return false;
            }
          });
        });
        $scope.cohort.name = useCustomCohortName ? customCohortName : $scope.cohort.name;
      }
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
        var checkboxes = $scope.search.checkboxes;
        var inactive = checkboxes.inactive.show = checkboxes.inactive.checked ? true : null;
        var intensive = checkboxes.intensive.show = checkboxes.intensive.checked ? true : null;
        var advisorLdapUid = checkboxes.advisorLdapUid.show = checkboxes.advisorLdapUid.checked ? checkboxes.advisorLdapUid.value : null;
        promise = studentSearchService.getStudents(
          $scope.search.options,
          inactive,
          intensive,
          advisorLdapUid,
          orderBy,
          offset,
          limit,
          true);
      } else if (isNaN($scope.cohort.code)) {
        promise = athleticsFactory.getTeam($scope.cohort.code, orderBy, offset, limit);
      } else {
        promise = filteredCohortFactory.getCohort($scope.cohort.code, orderBy, offset, limit);
      }
      return promise;
    };

    var isPaginationEnabled = function() {
      return _.includes([ 'search' ], $scope.cohort.code) || !isNaN($scope.cohort.code);
    };

    /**
     * @param  {Function}    callback    Follow up activity per caller
     * @return {void}
     */
    var listViewRefresh = function(callback) {
      // Pagination is not used on teams because student count is within reason.
      $scope.pagination.enabled = isPaginationEnabled();
      var pageNumber = $scope.pagination.enabled ? $scope.pagination.currentPage : 1;
      var limit = $scope.pagination.enabled ? $scope.pagination.itemsPerPage : Number.MAX_SAFE_INTEGER;
      var offset = pageNumber === 0 ? 0 : (pageNumber - 1) * limit;

      page.loading(true);
      getCohort($scope.orderBy.selected, offset, limit).then(function(response) {
        updateCohort(response.data);
        return callback();
      }).catch(function(err) {
        if (err.status === 404) {
          $location.replace().path('/404');
        } else {
          $scope.error = validationService.parseError(err);
          return callback(null);
        }
      });
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
      var selectedCodes = $scope.cohort.groupCodes ? _.map($scope.cohort.groupCodes, 'groupCode') : getCohortCriteria('groupCodes');
      initFilter('groupCodes', 'groupCode', selectedCodes, onClickOption);
      // Levels
      initFilter('levels', 'value', getCohortCriteria('levels'), onClickOption);
      // Majors (the 'Declared' and 'Undeclared' options are special)
      _.map($scope.search.options.majors, function(option) {
        if (option) {
          option.onClick = option.onClick || onClickSpecificMajor;
        }
      });
      initFilter('majors', 'name', getCohortCriteria('majors'));
      // Units
      initFilter('unitRanges', 'value', getCohortCriteria('unitRanges'), onClickOption);
      var checkbox = $scope.search.checkboxes.advisorLdapUid;
      var advisorUid = checkbox.value || getCohortCriteria('advisorLdapUid');
      if (advisorUid) {
        checkbox.show = checkbox.checked = true;
        checkbox.value = advisorUid;
        if (advisorUid !== authService.getMe().uid) {
          adminFactory.getUserProfile(advisorUid).then(function(response) {
            $scope.search.checkboxes.advisorLdapUid.label = response.data.firstName + '\'s Students';
          });
        }
      } else {
        checkbox.show = checkbox.checked = false;
      }
      // Ready for the world!
      return callback();
    };

    /**
     * Get ALL students of the cohort then render the scatterplot graph.
     *
     * @param  {Function}    callback      Standard callback function
     * @return {void}
     */
    var matrixViewRefresh = function(callback) {
      page.loading(true);
      getCohort(null, 0, $scope.pagination.noLimit).then(function(response) {
        updateCohort(response.data);
        var goToUserPage = function(uid) {
          $location.state($location.absUrl());
          $location.path('/student/' + uid);
          // The intervening visualizationService code moves out of Angular and into d3 thus the extra kick of $apply.
          $scope.$apply();
        };
        visualizationService.scatterplotRefresh($scope.cohort.students, goToUserPage, function(yAxisMeasure, studentsWithoutData) {
          $scope.yAxisMeasure = yAxisMeasure;
          // List of students-without-data is rendered below the scatterplot.
          $scope.studentsWithoutData = studentsWithoutData;
        });
        return callback();
      }).catch(function(err) {
        if (err.status === 404) {
          $location.replace().path('/404');
        } else {
          $scope.error = validationService.parseError(err);
          return callback();
        }
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
          checkMatrixViewThreshold();
          page.loading(false);
        });
      } else {
        $scope.pagination.enabled = true;

        var handleSuccess = function(response) {
          updateCohort(response.data);
        };

        var handleError = function(err) {
          $scope.error = validationService.parseError(err);
        };
        var checkboxes = $scope.search.checkboxes;
        var pageNumber = $scope.pagination.currentPage;
        var offset = pageNumber < 2 ? 0 : (pageNumber - 1) * $scope.pagination.itemsPerPage;

        // Perform the query
        page.loading(true);
        studentSearchService.getStudents(
          $scope.search.options,
          checkboxes.inactive.checked ? true : null,
          checkboxes.intensive.checked ? true : null,
          checkboxes.advisorLdapUid.checked ? checkboxes.advisorLdapUid.value : null,
          $scope.orderBy.selected,
          offset,
          $scope.pagination.itemsPerPage,
          true
        ).then(handleSuccess, handleError).then(function() {
          checkMatrixViewThreshold();
          page.loading(false);
        });
      }
    };

    /**
     * Certain query args will cause 'selected=true' in search filters.
     *
     * @param  {String}     filterName    Represents a dropdown (ie, search filter) used to search by teamGroup, etc.
     * @param  {Array}      selected      Request parameter value(s)
     * @return {void}
     */
    var preset = function(filterName, selected) {
      if (!_.isEmpty(selected)) {
        _.each($scope.search.options[filterName], function(option) {
          if (option) {
            var match = _.isString(selected) ? selected === option.value : _.includes(selected, option.value);
            if (match) {
              option.selected = true;
              $scope.search.count[filterName] += 1;
            }
          }
        });
      }
    };

    /**
     * Invoked when state is initializing. Preset filters and search criteria prior to cohort API call.
     *
     * @param  {Object}       args       Selections from search filters
     * @return {void}
     */
    var presetSearchFilters = function(args) {
      if (isNaN($scope.cohort.code) && !_.isEmpty(args)) {
        if ($scope.cohort.code === 'search') {
          _.each(filters, function(key, filterName) {
            preset(filterName, args[key]);
          });
        } else {
          // code is a team_code
          _.each($scope.search.options.groupCodes, function(option) {
            if ($scope.cohort.code === option.teamCode) {
              option.selected = true;
              $scope.search.count.groupCodes += 1;
            }
          });
        }
      }
      if (args.o && _.find($scope.orderBy.options, ['value', args.o])) {
        $scope.orderBy.selected = args.o;
      }
      if (args.p && !isNaN(args.p)) {
        $scope.pagination.currentPage = parseInt(args.p, 10);
      }
      if (args.v && _.includes(['list', 'matrix'], args.v)) {
        $scope.tab = args.v;
      }
    };

    /**
     * List view is paginated but Matrix view must show all users. Lazy load the Matrix tab.
     *
     * @param  {String}    tabName          Name of tab clicked by user
     * @return {void}
     */
    $scope.onTab = function(tabName) {
      $scope.tab = tabName;
      $location.search('v', $scope.tab);
      // Lazy load matrix data
      if (tabName === 'matrix' && !$scope.matrix) {
        matrixViewRefresh(function() {
          page.loading(false);
        });
      } else if (tabName === 'list') {
        // Restore pagination; fortunately, 'currentPage' persists.
        $scope.pagination.enabled = isPaginationEnabled();
        if ($scope.pagination.enabled && $scope.pagination.currentPage > 1 && $scope.cohort.students.length > 50) {
          var start = ($scope.pagination.currentPage - 1) * 50;
          $scope.cohort.students = _.slice($scope.cohort.students, start, start + 50);
        }
      }
    };

    /**
     * Search per filter criteria.
     *
     * @return {void}
     */
    $scope.applyFilters = function() {
      $scope.isCreateCohortMode = false;
      $scope.search.dropdown = defaultDropdownState();
      $rootScope.$broadcast('resetCuratedCohortSelector');
      // Refresh search results
      $scope.cohort.code = 'search';
      $rootScope.pageTitle = 'Search';
      $scope.pagination.currentPage = 1;
      $location.search('c', $scope.cohort.code);
      $location.search('p', $scope.pagination.currentPage);
      if ($scope.tab === 'list') {
        nextPage();
      } else {
        matrixViewRefresh(function() {
          page.loading(false);
        });
      }
    };

    $scope.$watch('orderBy.selected', function(value) {
      if (value && !page.isLoading()) {
        $location.search('o', $scope.orderBy.selected);
        $scope.pagination.currentPage = 1;
        nextPage();
      }
    });

    $scope.$watch('pagination.currentPage', function() {
      if (!page.isLoading()) {
        $location.search('p', $scope.pagination.currentPage);
      }
    });

    $scope.enableApplyButton = function() {
      // Disable button if page is loading or no filter criterion is selected
      var enable = true;
      if (page.isLoading() || $scope.isSaving) {
        enable = false;
      } else {
        var count = $scope.search.count;
        var selectedOptionsCount = count.gpaRanges + count.groupCodes + count.levels + count.majors + count.unitRanges;
        enable = selectedOptionsCount ||
          $scope.search.checkboxes.intensive.checked ||
          $scope.search.checkboxes.inactive.checked ||
          $scope.search.checkboxes.advisorLdapUid.checked;
      }
      return enable;
    };

    var getMajors = function(callback) {
      studentFactory.getRelevantMajors().then(function(majorsResponse) {
        // Remove '*-undeclared' options in favor of generic 'Undeclared'
        var majors = _.filter(majorsResponse.data, function(major) {
          return !major.match(/undeclared/i);
        });
        majors = _.map(majors, function(name) {
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

    // Grades deserving alerts: D(+/-), F, I, NP.
    var alertGrades = /^[DFIN]/;

    $scope.isAlertGrade = function(grade) {
      return grade && alertGrades.test(grade);
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

      athleticsFactory.getAllTeamGroups().then(function(teamsResponse) {
        var groupCodes = teamsResponse.data;

        getMajors(function(majors) {
          var decorate = utilService.decorateOptions;
          $scope.search.options = {
            gpaRanges: decorate(studentFactory.getGpaRanges(), 'name'),
            groupCodes: decorate(groupCodes, 'groupCode'),
            levels: decorate(studentFactory.getStudentLevels(), 'name'),
            majors: decorate(majors, 'name'),
            unitRanges: decorate(studentFactory.getUnitRanges(), 'name')
          };
          // Filter options to 'selected' per request args
          presetSearchFilters(args);

          if ($scope.isCreateCohortMode) {
            initFilters(function() {
              page.loading(false);
            });
          } else {
            var render = $scope.tab === 'list' ? listViewRefresh : matrixViewRefresh;
            render(function() {
              initFilters(function() {
                $rootScope.pageTitle = $scope.isCreateCohortMode ? 'Create Filtered Cohort' : $scope.cohort.name || 'Search';
                checkMatrixViewThreshold();

                page.loading(false);

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
      }).catch(function(err) {
        if (err.status === 404) {
          $location.replace().path('/404');
        } else {
          $scope.error = validationService.parseError(err);
          page.loading(false);
        }
      });
    };

    /**
     * Reload page with newly created cohort.
     */
    $rootScope.$on('filteredCohortCreated', function(event, data) {
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
