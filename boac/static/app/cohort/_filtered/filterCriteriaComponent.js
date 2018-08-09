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

  var FilterCriteriaController = function($scope, filterCriteriaUtil, filterCriteriaService) {

    $scope.isLoadingCriteria = true;

    this.$onInit = function() {
      var filterCriteria = _.clone(this.cohort.filterCriteria);
      filterCriteriaService.getFilterDefinitions(function(availableFilters) {

        filterCriteriaUtil.initFiltersForDisplay(filterCriteria, availableFilters, function(addedFilters) {
          $scope.availableFilters = availableFilters;
          $scope.addedFilters = addedFilters;
          $scope.isLoadingCriteria = false;
        });
      });
    };

    /**
     * Button to add a "draft" filter to the list of added-filters.
     */
    $scope.addButton = {
      onClick: function(draftFilter) {
        var primary = draftFilter.primary;
        var filterDefinition = _.find($scope.availableFilters, ['key', primary.key]);
        var value = null;

        if (filterDefinition.depth === 1) {
          value = _.get(primary, 'value') || true;
        } else if (draftFilter.primary.depth === 2) {
          value = draftFilter.secondary.value;
        } else {
          throw new Error('Cohort-filter definition depth is not yet supported: ' + d.depth);
        }
        $scope.addedFilters.push({
          name: primary.name,
          value: value
        });

        filterCriteriaUtil.updateFiltersForDisplay($scope.addedFilters, $scope.availableFilters, function(addedFilters) {
          $scope.addedFilters = addedFilters;
          // Reset the unsaved-filter
          draftFilter.primary = null;
          draftFilter.secondary = null;
        });
      },
      show: function(draftFilter) {
        var show = false;
        var primary = _.get(draftFilter, 'primary');
        if (primary) {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          show = primary.depth === 1 || (primary.depth === 2 && _.get(draftFilter, 'secondary.value'));
        }
        return !!show;
      }
    };

    /**
     * Button to search for students based on added filters.
     */
    $scope.applyButton = {
      disabled: function(addedFilters, draftFilter) {
        return !addedFilters.length && !_.get(draftFilter, 'primary');
      },
      onClick: function() {
        _.noop();
      },
      show: function(addedFilters, draftFilter) {
        return !_.isEmpty(addedFilters) && _.isEmpty(draftFilter);
      }
    };

    /**
     * Button to remove an added filter.
     */
    $scope.removeButton = {
      onClick: function(indexOfAddedFilter) {
        _.pullAt($scope.addedFilters, [ indexOfAddedFilter ]);
      }
    };

    /**
     * Button to save/update the cohort in the db.
     */
    $scope.saveButton = {
      disabled: function() {
        return true;
      },
      onClick: function(draftFilter) {
        draftFilter.secondary = null;
        draftFilter.primary = null;
      },
      show: function(draftFilter) {
        var show = false;
        var primary = _.get(draftFilter, 'primary');
        if (primary) {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          show = !!(primary.depth === 1 && primary.value) || (primary.depth === 2 && _.get(draftFilter, 'secondary.value'));
        }
        return show;
      }
    };
  };

  angular.module('boac').component('filterCriteria', {
    bindings: {
      cohort: '='
    },
    controller: FilterCriteriaController,
    templateUrl: '/static/app/cohort/_filtered/filterCriteria.html'
  });

}(window.angular));
