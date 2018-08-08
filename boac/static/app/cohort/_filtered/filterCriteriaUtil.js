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

    var constructFilterCriteria = function(savedFilters) {
      var definitions = filterCriteriaService.filterDefinitions();
      var filterCriteria = {};
      // Initialize per definitions
      _.each(definitions, function(d) {
        filterCriteria[d.key] = d.defaultValue;
      });
      // Update based on savedFilters
      _.each(filterCriteria, function(value, key) {
        var definition = _.find(definitions, ['key', key]);
        var values = [];
        _.each(savedFilters, function(savedFilter) {
          if (definition.name === savedFilter.name) {
            values.push(savedFilter.value);
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
     * @param  {Object}     filterCriteria    Has filter-criteria of saved search.
     * @param  {Function}   callback          Standard callback
     * @return {Object}                       Bundle with criteria-reference object and selected cohort filter criteria.
     */
    var getSavedFiltersForDisplay = function(filterCriteria, callback) {
      filterCriteriaService.getFilterDefinitions(function(filterDefinitions) {
        var savedFilters = [];

        _.each(filterCriteria, function(selectedOptions, key) {
          // If 'options' is an object then create an array of one.
          var values = utilService.asArray(selectedOptions);
          if (utilService.lenientBoolean(values)) {
            var d = _.find(filterDefinitions, ['key', key]);
            // If multiple values are mapped to a key (eg, multiple gpaRanges) then we display multiple rows.
            var savedFilter = {
              name: d.name,
              values: values
            };
            if (d.depth === 1) {
              d.disabled = true;
            } else if (d.depth === 2) {
              var subOption = _.find(d.options, ['key', key]);
              if (subOption) {
                subOption.disabled = true;
              }
            } else {
              throw new Error('Cohort-filter definition depth is not yet supported: ' + d.depth);
            }
            savedFilters.push(savedFilter);
          }
        });
        return callback({
          filterDefinitions: filterDefinitions,
          savedFilters: savedFilters
        });
      });
    };

    return {
      constructFilterCriteria: constructFilterCriteria,
      getSavedFiltersForDisplay: getSavedFiltersForDisplay
    };
  });

}(window.angular));
