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

  var FilterCriteriaController = function(
    $rootScope,
    $scope,
    cohortUtils
  ) {

    $scope.filters = {
      added: [],
      definitions: [],
      draft: null,
      isLoading: true
    };

    var redrawButtons = function(isInitPhase) {
      _.each($scope.buttons, function(button) {
        button.redraw(isInitPhase);
      });
    };

    $scope.onDraftFilterClick = function(option) {
      if (option && !option.disabled) {
        // Init
        $scope.filters.draft = _.clone(option);
        // Is there a subcategory?
        var type = _.get(option, 'type');
        if (type === 'range') {
          // Range form elements
          $scope.filters.draft.subcategory = {
            error: null,
            name: null,
            onChange: function() {
              var start = _.upperCase(_.get($scope.filters.draft, 'subcategory.range.start'));
              var stop = _.upperCase(_.get($scope.filters.draft, 'subcategory.range.stop'));
              var error = start.length && stop.length && start > stop ? 'Invalid range' : null;
              if (error) {
                $scope.filters.draft.subcategory.error = error;
              } else {
                $scope.filters.draft.subcategory.error = null;
                $scope.filters.draft.subcategory.name = cohortUtils.getRangeDisplayName(start, stop);
                $scope.filters.draft.subcategory.value = [start, stop];
              }
              $scope.buttons.addButton.disabled = _.isEmpty(start) || _.isEmpty(stop) || start > stop;
            },
            range: {
              lower: null,
              upper: null
            },
            value: null
          };
          $scope.buttons.addButton.show = $scope.buttons.addButton.disabled = true;
        } else if (type === 'boolean') {
          $scope.buttons.addButton.show = true;
        }
        redrawButtons();
      }
    };

    $scope.onDraftSubCategoryClick = function(option) {
      if (option !== null && !option.disabled) {
        $scope.filters.draft.subcategory = option;
        $scope.buttons.addButton.show = true;
        $scope.buttons.cancelButton.show = true;
      }
    };

    var resetDraftFilter = function() {
      $scope.filters.draft = null;
      $scope.buttons.addButton.show = false;
      $scope.buttons.cancelButton.show = false;
    };

    this.$onInit = function() {
      var filterCategories = _.clone(this.filterCategories);
      var filterCriteria = _.clone(this.cohort.filterCriteria);

      $scope.callbacks = this.callbacks;
      $scope.filters.definitions = [];

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
        $scope.filters.added = addedFilters;
        redrawButtons(true);
        $scope.filters.isLoading = false;
      });
    };

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

    $scope.buttons = {
      addButton: {
        // Button to add a "draft" filter to the list of added-filters.
        onClick: function() {
          var addedFilter = _.clone($scope.filters.draft);
          resetDraftFilter();

          updateDisableAfterAddOrRemove(addedFilter, true);
          $scope.filters.added = cohortUtils.sortAddedFilters($scope.filters.definitions, _.union($scope.filters.added, [ addedFilter ]));
          $scope.buttons.applyButton.show = true;
        },
        show: false,
        redraw: function() {
          // addButton.show is managed in the onClick() of other buttons.
        }
      },
      applyButton: {
        // Button to search for students based on added filters.
        disabled: true,
        onClick: function() {
          var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
          $scope.callbacks.executeSearch(filterCriteria);
          $scope.buttons.saveButton.show = true;
        },
        show: false,
        redraw: function(isInitPhase) {
          // Show 'Apply' button (ie, perform search) if non-empty criteria and no "draft" filter is in-progress.
          var emptyDraft = !_.get($scope.filters.draft, 'key');
          var show = $scope.buttons.applyButton.show = !isInitPhase && emptyDraft && $scope.filters.added.length;
          $scope.buttons.applyButton.disabled = !show && emptyDraft && !$scope.filters.added.length;
        }
      },
      cancelButton: {
        // Button to reset draft filter.
        onClick: function() {
          resetDraftFilter();
          redrawButtons();
        },
        show: false,
        redraw: function(isInitPhase) {
          $scope.buttons.cancelButton.show = !isInitPhase && _.get($scope.filters.draft, 'key');
        }
      },
      removeButton: {
        // Button to remove an added filter.
        onClick: function(indexOfAddedFilter) {
          var removedFilter = _.pullAt($scope.filters.added, [ indexOfAddedFilter ]);
          if (removedFilter.length) {
            updateDisableAfterAddOrRemove(removedFilter[0], false);
            $scope.buttons.applyButton.redraw(false);
          }
          $scope.buttons.saveButton.redraw(false);
        },
        show: true,
        redraw: function() {
          // 'show' is always true
        }
      },
      saveButton: {
        // Button to save/update the cohort in the db.
        disabled: false,
        onClick: function(openCreateCohortModal) {
          $scope.buttons.saveButton.disabled = true;
          var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
          openCreateCohortModal(filterCriteria, function(cohort) {
            $scope.buttons.saveButton.disabled = false;
            if (cohort) {
              $scope.buttons.saveButton.show = false;
              $scope.callbacks.onSave(cohort);
            }
          });
        },
        show: false,
        redraw: function(isInitPhase) {
          // We set 'show' to true when user clicks Apply. We set 'show' to false if filters are altered.
          if (isInitPhase && _.size($scope.filters.added)) {
            $scope.buttons.saveButton.show = true;
          } else if (_.isEmpty($scope.filters.added) || _.get($scope.filters.draft, 'key')) {
            $scope.buttons.saveButton.show = false;
          }
        }
      }
    };
  };

  angular.module('boac').component('filterCriteria', {
    bindings: {
      callbacks: '=',
      cohort: '=',
      filterCategories: '='
    },
    controller: FilterCriteriaController,
    templateUrl: '/static/app/cohort/filtered/filterCriteria.html'
  });

}(window.angular));
