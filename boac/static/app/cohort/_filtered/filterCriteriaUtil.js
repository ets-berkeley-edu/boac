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

    var constructFilterCriteria = function(addedFilters) {
      var definitions = filterCriteriaService.filterDefinitions();
      var filterCriteria = {};
      // Initialize per definitions
      _.each(definitions, function(d) {
        filterCriteria[d.key] = d.defaultValue;
      });
      // Update based on addedFilters
      _.each(filterCriteria, function(value, key) {
        var definition = _.find(definitions, ['key', key]);
        var values = [];
        _.each(addedFilters, function(addedFilter) {
          if (definition.name === addedFilter.name) {
            values.push(addedFilter.value);
          }
        });
        filterCriteria[key] = definition.handler(values);
      });
      return filterCriteria;
    };

    /**
     * Cohort's existing filter-criteria are converted to an array of arrays. For example, if criteria has
     * majors: [a, b, c] then this function will prepare three rows.
     *
     * The value of the secondary dropdown-select is always an array with a single string. For example,
     * the 'Levels' filter has secondary dropdown-select with four options but user can only choose one so
     * 'secondaryOption' below is an array of length == 1.
     *
     * @param  {Object}     filterCriteria    Has filter-criteria of saved search.
     * @param  {Object}     availableFilters  Used to render 'Add filter' options (some options are disabled)
     * @param  {Function}   callback          Standard callback
     * @return {Object}                       Bundle with criteria-reference object and selected cohort filter criteria.
     */
    var initFiltersForDisplay = function(filterCriteria, availableFilters, callback) {
      var addedFilters = [];

      _.each(filterCriteria, function(selectedOptions, key) {
        if (utilService.lenientBoolean(selectedOptions)) {
          var d = _.find(availableFilters, ['key', key]);
          var handled = d.handler(selectedOptions);
          handled = Array.isArray(handled) ? handled : [ handled ];
          _.each(handled, function(value) {
            if (value) {
              var addedFilter = {
                name: d.name,
                value: value
              };
              if (d.depth === 1) {
                d.disabled = true;
              } else if (d.depth === 2) {
                var secondaryOption = _.find(d.options, ['value', value]);
                if (secondaryOption) {
                  addedFilter.secondaryName = secondaryOption.name;
                  secondaryOption.disabled = true;
                }
              } else {
                throw new Error('Cohort-filter definition depth is not yet supported: ' + d.depth);
              }
              addedFilters.push(addedFilter);
            }
          });
        }
      });
      return callback(addedFilters);
    };

    var updateFiltersForDisplay = function(addedFilters, availableFilters, callback) {
      var filterCriteria = constructFilterCriteria(addedFilters);

      initFiltersForDisplay(filterCriteria, availableFilters, function(updatedFilters) {
        return callback(updatedFilters);
      });
    };

    return {
      constructFilterCriteria: constructFilterCriteria,
      initFiltersForDisplay: initFiltersForDisplay,
      updateFiltersForDisplay: updateFiltersForDisplay
    };
  });

}(window.angular));
