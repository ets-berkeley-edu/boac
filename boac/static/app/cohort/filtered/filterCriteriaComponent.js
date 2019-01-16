/**
 * Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.
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

  var FilterCriteriaController = function(
    $rootScope,
    $scope,
    $timeout,
    cohortUtils,
    filteredCohortFactory,
    utilService
  ) {

    $scope.filters = {
      added: [],
      definitions: [],
      isEditMode: false,
      isLoading: true
    };

    /**
     * @param  {Object}    updatedFilter    Filter (eg, Levels) with a newly selected subcategory or boolean value.
     * @param  {Boolean}   disable          True or false to disable or enable the select menu option.
     * @return {void}
     */
    var updateDisableAfterAddOrRemove = function(updatedFilter, disable) {
      var filter = _.find($scope.filters.definitions, ['key', updatedFilter.key]);
      if (updatedFilter.type === 'array') {
        // Disable option in sub-categories.
        var value = updatedFilter.subcategory.value;
        var option = _.find(filter.options, ['value', value]);
        if (option) {
          option.disabled = disable;
        }
        var disabledCount = _.size(_.filter(filter.options, 'disabled'));
        filter.disabled = disabledCount === _.size(filter.options);
      } else {
        filter.disabled = disable;
      }
    };

    /**
     * @param  {String}    key    Primary key (eg, unitRange) of desired filter definition.
     * @return {Object}           Matching filter definition
     */
    var getFilterDefinition = function(key) {
      return _.find($scope.filters.definitions, ['key', key]);
    };

    /**
     * @param  {String}    key                 Primary key of filter definition
     * @param  {String}    subcategoryValue    Value of targeted select menu option
     * @param  {String}    disabled            True of false will be applied to select menu option
     * @return {void}
     */
    var setFilterOptionDisabled = function(key, subcategoryValue, disabled) {
      var matchingOption = _.find(getFilterDefinition(key).options, ['value', subcategoryValue]);
      _.set(matchingOption, [ 'disabled' ], disabled ? true : null);
    };

    /**
     * @param  {Object}      filters    The filter criteria of a cohort or search.
     * @return {Object}                 The provided filters sorted and decorated for display on the page.
     */
    var decorateAddedFilters = function(filters) {
      return _.merge(cohortUtils.sortAddedFilters($scope.filters.definitions, filters), {
        buttons: {
          cancel: {
            onClick: function(row) {
              setFilterOptionDisabled(row.key, row.previousSubcategory.value, true);
              row.subcategory = row.previousSubcategory;
              row.isEditMode = $scope.filters.isEditMode = row.error = null;
              $scope.filterUpdateStatus = 'Cancelled';
            }
          },
          edit: {
            onClick: function(row) {
              var onOptionClick = function(subcategory) {
                row.subcategory = subcategory;
              };
              var definition = getFilterDefinition(row.key);
              // Populate dropdown with filter options
              setFilterOptionDisabled(row.key, row.subcategory.value, false);
              _.merge(row, {
                isMenuOpen: true,
                onOptionClick: onOptionClick,
                options: definition.options,
                previousSubcategory: row.subcategory,
                subcategory: row.subcategory,
                subcategoryHeader: definition.subcategoryHeader
              });
              $scope.draft = null;
              $scope.filters.isEditMode = row.isEditMode = true;
            }
          },
          remove: {
            onClick: function(index) {
              var removed = _.pullAt($scope.filters.added, [ index ]);
              if (removed.length) {
                updateDisableAfterAddOrRemove(removed[0], false);
                $scope.search.buttons.apply.redraw();
                $scope.search.buttons.save.show = false;
                $scope.filterUpdateStatus = removed[0].name + ' filter removed';
              }
            }
          },
          update: {
            onClick: function(row) {
              row.error = null;
              setFilterOptionDisabled(row.key, row.subcategory.value, true);
              setFilterOptionDisabled(row.key, row.previousSubcategory.value, false);
              $scope.search.buttons.apply.show = row.previousSubcategory !== row.subcategory;
              if (row.type === 'range') {
                var start = row.subcategory.range.start;
                var stop = row.subcategory.range.stop;
                if (_.isEmpty(start) || _.isEmpty(stop)) {
                  row.error = utilService.uibPopoverError('Required field(s) are blank. Please fix.');
                } else if (start > stop) {
                  row.error = utilService.uibPopoverError('The range values \'' + start + '\' and \'' + stop + '\' must be in ascending order.');
                } else {
                  row.subcategory.name = cohortUtils.getRangeDisplayName(start, stop);
                  row.subcategory.value = [start, stop];
                }
              }
              if (!row.error) {
                $scope.filterUpdateStatus = row.name + ' filter updated';
                row.previousSubcategory = null;
                $scope.filters.isEditMode = row.isEditMode = false;
              }
            }
          }
        }
      });
    };

    /**
     * @return {Object}  The set of buttons adjacent to 'Add a filter' dropdown menu.
     */
    var getDraftButtons = function() {
      return {
        buttons: {
          add: {
            disabled: false,
            onClick: function() {
              var addedFilter = _.clone($scope.draft);

              $scope.draft = null;
              $scope.search.buttons.save.show = false;
              updateDisableAfterAddOrRemove(addedFilter, true);
              $scope.filters.added = decorateAddedFilters(_.union($scope.filters.added, [ addedFilter ]));
              $scope.search.buttons.apply.show = true;
              $scope.filterUpdateStatus = addedFilter.name + ' filter added';
            },
            show: false
          },
          cancel: {
            onClick: function() {
              $scope.draft = null;
              $scope.search.buttons.apply.redraw();
              $scope.filterUpdateStatus = 'Cancelled';
            },
            show: false
          }
        }
      };
    };

    var initDraft = function(filterDefinition) {
      var draft = _.merge(_.clone(filterDefinition), getDraftButtons());
      var type = _.get(draft, 'type');
      if (type === 'range') {
        // Range form elements
        draft.subcategory = {
          error: null,
          name: null,
          onChange: function() {
            var start = _.upperCase(_.get(draft, 'subcategory.range.start'));
            var stop = _.upperCase(_.get(draft, 'subcategory.range.stop'));
            var error = start.length && stop.length && start > stop;
            if (error) {
              draft.subcategory.error = 'The range values \'' + start + '\' and \'' + stop + '\' must be in ascending order.';
            } else {
              draft.subcategory.error = null;
              draft.subcategory.name = cohortUtils.getRangeDisplayName(start, stop);
              draft.subcategory.value = [start, stop];
            }
            draft.buttons.add.disabled = _.isEmpty(start) || _.isEmpty(stop) || start > stop;
          },
          range: {
            lower: null,
            upper: null
          },
          value: null
        };
        draft.buttons.add.show = draft.buttons.add.disabled = true;
      } else if (type === 'boolean') {
        draft.buttons.add.show = true;
      }
      return draft;
    };

    var onSuccessfulCohortSave = function(cohort) {
      // If user clicked 'Cancel' then do nothing.
      if (cohort) {
        $scope.search.cohort = cohort;
        $scope.callbacks.onSave($scope.search.cohort);
        $scope.acknowledgeSave = true;
        $timeout(function() {
          $scope.search.buttons.save.show = $scope.acknowledgeSave = false;
        }, 2000);
      }
    };

    var initSearch = function(search, allowSave) {
      return _.merge(search, {
        buttons: {
          apply: {
            // Button to search for students based on added filters.
            onClick: function() {
              var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
              $scope.callbacks.applyFilters(filterCriteria);
            },
            show: false,
            redraw: function() {
              // Show 'Apply' button (ie, perform search) if non-empty criteria and no "draft" filter is in-progress.
              var emptyDraft = !_.get($scope.draft, 'key');
              $scope.search.buttons.apply.show = emptyDraft && $scope.filters.added.length;
            }
          },
          save: {
            onClick: function(openCreateCohortModal) {
              var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
              var cohortId = $scope.search.cohort.id;

              if (cohortId) {
                var count = $scope.search.results.totalStudentCount;
                filteredCohortFactory.update(cohortId, null, filterCriteria, count, onSuccessfulCohortSave);
              } else {
                openCreateCohortModal(filterCriteria, onSuccessfulCohortSave);
              }
            },
            show: allowSave
          }
        }
      });
    };

    $scope.onDraftFilterClick = function(filterDefinition) {
      if (filterDefinition && !filterDefinition.disabled) {
        $scope.draft = initDraft(filterDefinition);
        $scope.search.buttons.apply.redraw();
        $scope.draft.buttons.cancel.show = true;
      }
    };

    $scope.onDraftSubcategoryOptionClick = function(option) {
      if (option !== null && !option.disabled) {
        $scope.draft.subcategory = option;
        $scope.draft.buttons.add.show = true;
      }
    };

    /**
     * Invoked on page load only. If user has just clicked 'Create New Cohort' then the 'cohort' object is undefined.
     * If user is viewing an existing cohort then s/he can save changes if and only if 'isOwnedByCurrentUser' is true.
     * We never offer a 'Save As' option therefore other people's cohorts are strictly read-only.
     *
     * @returns {void}
     */
    this.$onInit = function() {
      var filterCategories = _.clone(this.filterCategories);
      var filterCriteria = _.clone(this.search.filterCriteria);
      var isOwnedByCurrentUser = _.get(this.search.cohort, 'isOwnedByCurrentUser');
      // See documentation above
      $scope.allowEdits = _.isNil(isOwnedByCurrentUser) || isOwnedByCurrentUser;
      $scope.callbacks = this.callbacks;
      $scope.filters.definitions = [];
      $scope.search = initSearch(this.search, this.allowSave);

      _.each(filterCategories, function(category, index) {
        _.each(category, function(definition) {
          $scope.filters.definitions.push(definition);
        });
        var isLast = index === filterCategories.length - 1;
        if (!isLast) {
          // Null causes divider in filter dropdown
          $scope.filters.definitions.push(null);
        }
      });
      cohortUtils.initFiltersForDisplay(filterCriteria, $scope.filters.definitions, function(addedFilters) {
        $scope.filters.added = decorateAddedFilters(addedFilters);
        $scope.filters.isLoading = false;
      });
    };
  };

  angular.module('boac').component('filterCriteria', {
    bindings: {
      allowSave: '=',
      callbacks: '=',
      filterCategories: '=',
      search: '='
    },
    controller: FilterCriteriaController,
    templateUrl: '/static/app/cohort/filtered/filterCriteria.html'
  });

}(window.angular));
