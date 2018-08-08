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

  angular.module('boac').service('filterCriteriaUtil', function(filterCriteriaService, utilService) {

    /**
     * Cohort's existing filter-criteria are converted to an array of arrays. For example, if criteria has
     * majors: [a, b, c] then this function will prepare three rows.
     *
     * @param  {Object}     cohort            Has filter-criteria of saved search.
     * @param  {Function}   callback          Standard callback
     * @return {Object}                       Bundle with available and selected cohort filter criteria.
     */
    var getCriteriaForDisplay = function(cohort, callback) {
      filterCriteriaService.getFilterCriteriaRef(function(criteriaRef) {
        var availableFilters = criteriaRef;
        var selectedFilters = [];

        _.each(cohort.filterCriteria, function(options, key) {
          // If 'options' is an object then create an array of one.
          var values = utilService.asArray(options);
          if (_.size(values)) {
            var ref = _.find(criteriaRef, ['value', key]);
            _.each(values, function(value) {
              // If multiple values are mapped to a key (eg, multiple gpaRanges) then we display multiple rows.
              var columns = [];
              columns.push(ref.name);
              if (ref.depth === 1) {
                ref.disabled = true;
              } else if (ref.depth === 2) {
                columns.push(value);
                var subOption = _.find(ref.options, ['value', value]);
                if (subOption) {
                  subOption.disabled = true;
                }
              } else if (ref.depth > 2) {
                // TODO: For now, no criteria definitions have depth > 2.
              }
              selectedFilters.push(columns);
            });
          }
        });
        return callback({
          available: availableFilters,
          selected: selectedFilters
        });
      });
    };

    return {
      getCriteriaForDisplay: getCriteriaForDisplay
    };
  });

  var FilterCriteriaController = function($scope, filterCriteriaUtil) {

    var filterCriteria = null;

    $scope.isLoadingCriteria = true;

    this.$onInit = function() {
      filterCriteria = _.clone(this.cohort.filterCriteria);

      filterCriteriaUtil.getCriteriaForDisplay(this.cohort, function(criteria) {
        $scope.criteria = criteria;
        $scope.isLoadingCriteria = false;
      });
    };

    $scope.addButton = {
      onClick: function(menu) {
        if (menu.primary.depth === 1) {
          filterCriteria[menu.primary.value] = true;
        } else if (menu.primary.depth === 2) {
          filterCriteria[menu.primary.value] = menu.secondary.value;
        }
        filterCriteriaUtil.getCriteriaForDisplay({filterCriteria: filterCriteria}, function(criteria) {
          $scope.criteria = criteria;
          menu.primary = null;
          menu.secondary = null;
        });
      },
      show: function(menu) {
        var show = false;
        var primary = _.get(menu, 'primary');
        if (primary) {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          show = !!(primary.depth === 1 && primary.value) || (primary.depth === 2 && _.get(menu, 'secondary.value'));
        }
        return show;
      }
    };

    $scope.applyButton = {
      disable: function() {
        return true;
      },
      onClick: function() {
        _.noop();
      },
      show: function(menu) {
        var show = false;
        var primary = _.get(menu, 'primary');
        if (primary) {
          // Show 'Add' button if and only if user has drilled down to a valid selection.
          show = !!(primary.depth === 1 && primary.value) || (primary.depth === 2 && _.get(menu, 'secondary.value'));
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
