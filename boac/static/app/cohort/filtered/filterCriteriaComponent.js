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
    cohortUtils,
    filteredCohortFactory
  ) {

    $scope.filters = {
      added: [],
      definitions: [],
      isEditMode: false,
      isLoading: true
    };

    var redrawButtons = function(isInitPhase) {
      var inProgressDraft = _.get($scope.draft, 'key');
      $scope.buttons.cancelDraftFilter.show = !isInitPhase && inProgressDraft;
      $scope.buttons.apply.redraw(isInitPhase);
    };

    $scope.onDraftFilterClick = function(option) {
      if (option && !option.disabled) {
        // Init
        $scope.draft = _.clone(option);
        // Is there a subcategory?
        var type = _.get(option, 'type');
        if (type === 'range') {
          // Range form elements
          $scope.draft.subcategory = {
            error: null,
            name: null,
            onChange: function() {
              var start = _.upperCase(_.get($scope.draft, 'subcategory.range.start'));
              var stop = _.upperCase(_.get($scope.draft, 'subcategory.range.stop'));
              var error = start.length && stop.length && start > stop;
              if (error) {
                $scope.draft.subcategory.error = 'The range values \'' + start + '\' and \'' + stop + '\' must be in ascending order.';
              } else {
                $scope.draft.subcategory.error = null;
                $scope.draft.subcategory.name = cohortUtils.getRangeDisplayName(start, stop);
                $scope.draft.subcategory.value = [start, stop];
              }
              $scope.buttons.addFilter.disabled = _.isEmpty(start) || _.isEmpty(stop) || start > stop;
            },
            range: {
              lower: null,
              upper: null
            },
            value: null
          };
          $scope.buttons.addFilter.show = $scope.buttons.addFilter.disabled = true;
        } else if (type === 'boolean') {
          $scope.buttons.addFilter.show = true;
        }
        redrawButtons();
      }
    };

    $scope.onDraftSubcategoryOptionClick = function(option) {
      if (option !== null && !option.disabled) {
        $scope.draft.subcategory = option;
        $scope.buttons.addFilter.show = true;
        $scope.buttons.cancelDraftFilter.show = true;
      }
    };

    var resetDraftFilter = function() {
      $scope.draft = null;
      $scope.buttons.addFilter.show = false;
      $scope.buttons.cancelDraftFilter.show = false;
    };

    this.$onInit = function() {
      var filterCategories = _.clone(this.filterCategories);
      var filterCriteria = _.clone(this.filterCriteria);

      $scope.callbacks = this.callbacks;
      $scope.cohortId = this.cohortId;
      $scope.filters.definitions = [];
      $scope.allowEdits = this.allowEdits;
      $scope.buttons.saveCohort.show = this.allowSave;

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
      addFilter: {
        // Button to add a "draft" filter to the list of added-filters.
        onClick: function() {
          var addedFilter = _.clone($scope.draft);
          $scope.buttons.saveCohort.show = false;
          resetDraftFilter();
          updateDisableAfterAddOrRemove(addedFilter, true);
          $scope.filters.added = cohortUtils.sortAddedFilters($scope.filters.definitions, _.union($scope.filters.added, [ addedFilter ]));
          $scope.buttons.apply.show = true;
        },
        show: false
      },
      apply: {
        // Button to search for students based on added filters.
        disabled: true,
        onClick: function() {
          var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
          $scope.callbacks.applyFilters(filterCriteria);
        },
        show: false,
        redraw: function(isInitPhase) {
          // Show 'Apply' button (ie, perform search) if non-empty criteria and no "draft" filter is in-progress.
          var emptyDraft = !_.get($scope.draft, 'key');
          var show = $scope.buttons.apply.show = !isInitPhase && emptyDraft && $scope.filters.added.length;
          $scope.buttons.apply.disabled = !show && emptyDraft && !$scope.filters.added.length;
        }
      },
      cancelDraftFilter: {
        onClick: function() {
          resetDraftFilter();
          redrawButtons();
        },
        show: false
      },
      cancelEditAddedFilter: {
        onClick: function(row) {
          row.subcategory = row.original || row.subcategory;
          row.isEditMode = false;
          $scope.filters.isEditMode = false;
        }
      },
      editAddedFilter: {
        onClick: function(row) {
          var filter = _.find($scope.filters.definitions, ['key', row.key]);
          $scope.buttons.updateAddedFilter.disabled = true;
          row.options = filter.options;
          row.isMenuOpen = true;
          resetDraftFilter();
          row.original = row.subcategory;
          row.onOptionClick = function(unsaved) {
            row.subcategory = unsaved;
            $scope.buttons.updateAddedFilter.disabled = false;
          };
          $scope.filters.isEditMode = row.isEditMode = true;
        }
      },
      removeAddedFilter: {
        onClick: function(index) {
          var removed = _.pullAt($scope.filters.added, [ index ]);
          if (removed.length) {
            updateDisableAfterAddOrRemove(removed[0], false);
            $scope.buttons.apply.redraw(false);
          }
        }
      },
      saveCohort: {
        onClick: function(openCreateCohortModal) {
          var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.definitions, $scope.filters.added);
          var done = function(cohort) {
            if (cohort) {
              $scope.buttons.saveCohort.show = false;
              $scope.callbacks.onSave(cohort);
            }
            $scope.isSaving = false;
          };

          $scope.isSaving = true;
          if ($scope.cohortId) {
            // TODO: update db and update cache w.r.t cohort student_count
            filteredCohortFactory.update($scope.cohortId, null, filterCriteria).then(done);
          } else {
            openCreateCohortModal(filterCriteria, done);
          }
        },
        show: false
      },
      updateAddedFilter: {
        onClick: function(row) {
          $scope.buttons.apply.show = row.original !== row.subcategory;
          row.original = null;
          $scope.filters.isEditMode = row.isEditMode = false;
        }
      }
    };
  };

  angular.module('boac').component('filterCriteria', {
    bindings: {
      allowEdits: '=',
      allowSave: '=',
      callbacks: '=',
      cohortId: '=',
      filterCategories: '=',
      filterCriteria: '='
    },
    controller: FilterCriteriaController,
    templateUrl: '/static/app/cohort/filtered/filterCriteria.html'
  });

}(window.angular));
