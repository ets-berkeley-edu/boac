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

  var FilterCriteriaController = function($scope, cohortUtils) {

    $scope.filters = {
      added: [],
      available: [],
      draft: {
        primary: null,
        secondary: null
      },
      isLoading: true
    };

    var executeSearchFunction = null;

    var redrawButtons = function() {
      _.each($scope.buttons, function(button) {
        button.redraw();
      });
    };

    var onDraftFilterChange = function() {
      if (!$scope.filters.isLoading) {
        redrawButtons();
      }
    };

    this.$onInit = function() {
      var filterCriteria = _.clone(this.cohort.filterCriteria);
      executeSearchFunction = this.executeSearchFunction;

      $scope.$watch('filters.draft.primary', onDraftFilterChange);
      $scope.$watch('filters.draft.secondary', onDraftFilterChange);

      cohortUtils.initFilters(filterCriteria, function(addedFilters, availableFilters) {
        $scope.filters.available = availableFilters;
        $scope.filters.added = addedFilters;
        redrawButtons();
        $scope.filters.isLoading = false;
      });
    };

    var updateFilters = function(callback) {
      cohortUtils.updateFilters($scope.filters.added, function(addedFilters, availableFilters) {
        $scope.filters.added = addedFilters;
        $scope.filters.available = availableFilters;

        return callback();
      });
    };

    $scope.buttons = {
      addButton: {
        // Button to add a "draft" filter to the list of added-filters.
        onClick: function() {
          // TODO: No need for isLoading spinner if we do not re-init filterDefinitions in cohortUtils.updateFilters.
          $scope.filters.isLoading = true;

          var primary = $scope.filters.draft.primary;
          var filterDefinition = _.find($scope.filters.available, ['key', primary.key]);
          var value = null;

          if (filterDefinition.depth === 1) {
            value = _.get(primary, 'value') || true;
          } else if ($scope.filters.draft.primary.depth === 2) {
            value = $scope.filters.draft.secondary.value;
          } else {
            throw new Error('Cohort-filter definition depth is not yet supported: ' + d.depth);
          }
          $scope.filters.added.push({
            name: primary.name,
            value: value
          });

          updateFilters(function() {
            // Reset the unsaved-filter
            $scope.filters.draft.primary = null;
            $scope.filters.draft.secondary = null;
            $scope.filters.isLoading = false;
          });
        },
        show: false,
        redraw: function() {
          var depth = _.get($scope.filters.draft, 'primary.depth');
          var secondaryValue = _.get($scope.filters.draft, 'secondary.value');
          $scope.buttons.addButton.show = depth && (depth === 1 || (depth === 2 && secondaryValue));
        }
      },
      applyButton: {
        // Button to search for students based on added filters.
        disabled: true,
        onClick: function() {
          $scope.filters.isLoading = true;
          var filterCriteria = cohortUtils.constructFilterCriteria($scope.filters.added);
          executeSearchFunction(filterCriteria);
          $scope.filters.isLoading = false;
        },
        show: false,
        redraw: function() {
          // Show 'Apply' button (ie, perform search) if non-empty criteria and no "draft" filter is in-progress.
          var primary = _.get($scope.filters.draft, 'primary');
          var show = $scope.buttons.applyButton.show = !_.isEmpty($scope.filters.added) && !primary;
          $scope.buttons.applyButton.disabled = !show && !$scope.filters.added.length && !primary;
        }
      },
      cancelButton: {
        // Button to reset draft filter.
        onClick: function() {
          $scope.filters.draft = {
            primary: null,
            secondary: null
          };
        },
        show: false,
        redraw: function() {
          var depth = _.get($scope.filters.draft, 'primary.depth');
          var secondaryValue = _.get($scope.filters.draft, 'secondary.value');
          $scope.buttons.cancelButton.show = depth && (depth === 1 || (depth === 2 && secondaryValue));
        }
      },
      removeButton: {
        // Button to remove an added filter.
        onClick: function(indexOfAddedFilter) {
          _.pullAt($scope.filters.added, [ indexOfAddedFilter ]);
          updateFilters(_.noop);
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
          $scope.filters.draft.secondary = null;
          $scope.filters.draft.primary = null;
        },
        show: false,
        redraw: function() {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          var depth = _.get($scope.filters.draft, 'primary.depth');
          var secondaryValue = _.get($scope.filters.draft, 'secondary.value');
          var show = $scope.buttons.saveButton.show = depth && (depth === 1 && primary.value) || (depth === 2 && secondaryValue);
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
