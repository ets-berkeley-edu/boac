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
    filterCriteriaFactory,
    filterCriteriaService
  ) {

    $scope.filters = {
      added: [],
      available: [],
      draft: null,
      isLoading: true
    };

    var executeSearchFunction = null;

    var redrawButtons = function(isInitPhase) {
      _.each($scope.buttons, function(button) {
        button.redraw(isInitPhase);
      });
    };

    var onAddedFiltersChange = function() {
      $rootScope.$broadcast('filterCriteriaComponent.filters.added', $scope.filters.added);
    };

    var onDraftFilterChange = function() {
      if (!$scope.filters.isLoading) {
        redrawButtons();
      }
    };

    this.$onInit = function() {
      var filterCriteria = _.clone(this.cohort.filterCriteria);
      executeSearchFunction = this.executeSearchFunction;

      $scope.$watch('filters.added', onAddedFiltersChange);
      $scope.$watch('filters.draft', onDraftFilterChange);
      $scope.$watch('filters.draft.subCategory', onDraftFilterChange);

      filterCriteriaService.getAvailableFilters(filterCriteriaFactory.getFilterDefinitions(), function(availableFilters) {
        cohortUtils.initFiltersForDisplay(filterCriteria, availableFilters, function(addedFilters) {
          $scope.filters.available = availableFilters;
          $scope.filters.added = addedFilters;
          redrawButtons(true);
          $scope.filters.isLoading = false;
        });
      });
    };

    var updateDisableAfterAddOrRemove = function(updatedFilter, disable) {
      var depth = updatedFilter.depth;
      if (depth >= 3) {
        throw new Error('Cohort-filter definition depth is not yet supported: ' + d.depth);
      }
      var filter = _.find($scope.filters.available, ['key', updatedFilter.key]);
      if (depth === 1) {
        filter.disabled = disable;
      } else {
        // Depth is 2. Disable selected option in available-filters list.
        var value = updatedFilter.subCategory.value;
        var option = _.find(filter.options, ['value', value]);
        if (option) {
          option.disabled = disable;
        }
      }
    };

    $scope.buttons = {
      addButton: {
        // Button to add a "draft" filter to the list of added-filters.
        onClick: function() {
          var addedFilter = _.clone($scope.filters.draft);
          updateDisableAfterAddOrRemove(addedFilter, true);
          $scope.filters.added.push(addedFilter);
          $scope.filters.draft = null;
        },
        show: false,
        redraw: function(isInitPhase) {
          var depth = _.get($scope.filters.draft, 'depth');
          var secondaryValue = _.get($scope.filters.draft, 'subCategory.value');
          $scope.buttons.addButton.show = !isInitPhase && depth && (depth === 1 || (depth === 2 && secondaryValue));
        }
      },
      applyButton: {
        // Button to search for students based on added filters.
        disabled: true,
        onClick: function() {
          $scope.filters.isLoading = true;
          var filterCriteria = cohortUtils.toFilterCriteria($scope.filters.added);
          executeSearchFunction(filterCriteria);
          $scope.filters.isLoading = false;
        },
        show: false,
        redraw: function(isInitPhase) {
          // Show 'Apply' button (ie, perform search) if non-empty criteria and no "draft" filter is in-progress.
          var emptyDraft = !$scope.filters.draft;
          var show = $scope.buttons.applyButton.show = !isInitPhase && emptyDraft && $scope.filters.added.length;
          $scope.buttons.applyButton.disabled = !show && emptyDraft && !$scope.filters.added.length;
        }
      },
      cancelButton: {
        // Button to reset draft filter.
        onClick: function() {
          $scope.filters.draft = null;
        },
        show: false,
        redraw: function(isInitPhase) {
          var depth = _.get($scope.filters.draft, 'depth');
          var secondaryValue = _.get($scope.filters.draft, 'subCategory.value');
          $scope.buttons.cancelButton.show = !isInitPhase && depth && (depth === 1 || (depth === 2 && secondaryValue));
        }
      },
      removeButton: {
        // Button to remove an added filter.
        onClick: function(indexOfAddedFilter) {
          var removedFilter = _.pullAt($scope.filters.added, [ indexOfAddedFilter ]);
          if (removedFilter.length) {
            updateDisableAfterAddOrRemove(removedFilter[0], false);
          }
        },
        show: false,
        redraw: function() {
          $scope.buttons.removeButton.show = true;
        }
      },
      saveButton: {
        // Button to save/update the cohort in the db.
        disabled: true,
        onClick: function() {
          $scope.filters.draft = null;
        },
        show: false,
        redraw: function() {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          var depth = _.get($scope.filters.draft, 'depth');
          var subCategoryValue = _.get($scope.filters.draft, 'subCategory.value');
          var show = $scope.buttons.saveButton.show = depth && (depth === 1 && $scope.filters.draft.value) || (depth === 2 && subCategoryValue);
          $scope.buttons.saveButton.disabled = !show;
        }
      }
    };
  };

  angular.module('boac').component('filterCriteria', {
    bindings: {
      cohort: '=',
      executeSearchFunction: '='
    },
    controller: FilterCriteriaController,
    templateUrl: '/static/app/cohort/_filtered/filterCriteria.html'
  });

}(window.angular));
