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

  angular.module('boac').service('cohortUtils', function() {

    /**
     * @param  {Object}   obj   An array, object or nil.
     * @return {Array}          Nil if input is nil; same array if input is array; array of one if input is an object.
     */
    var asArray = function(obj) {
      if (_.isNil(obj)) {
        return null;
      }
      return Array.isArray(obj) ? obj : [ obj ];
    };

    var lenientBoolean = function(obj) {
      // Force array for dependable object structure
      var value = asArray(obj);
      return !_.isEmpty(value) && _.lowerCase(value[0]) !== 'false';
    };

    /**
     * @param  {Object}     filterDefinitions   An array including, for example, the 'majors' filter definition.
     * @param  {Object}     addedFilters        Filters added, by user, to search criteria.
     * @return {Object}                         Added filters in proper order.
     */
    var sortAddedFilters = function(filterDefinitions, addedFilters) {
      var sortOrder = _.map(filterDefinitions, 'key');

      return addedFilters.sort(function(f1, f2) {
        var index1 = sortOrder.indexOf(f1.key);
        var index2 = sortOrder.indexOf(f2.key);
        var diff = index1 - index2;

        if (diff === 0) {
          // Objects are from the same category (e.g., Majors) so we sort by sub-category.
          var p1 = _.get(f1, 'subcategory.position');
          var p2 = _.get(f2, 'subcategory.position');

          diff = _.isInteger(p1) && _.isInteger(p2) ? p1 - p2 : f1.value - f2.value;
        }
        return diff;
      });
    };

    /**
     * @param  {Object}     filterDefinition    For example, definition of the 'majors' filter option.
     * @param  {Object}     queryArg            HTTP request parameter.
     * @return {Object}                         Value converted according to filter definition (e.g., 1 becomes 'true').
     */
    var translateQueryArg = function(filterDefinition, queryArg) {
      var result;
      var type = filterDefinition.type;
      if (_.isNil(queryArg)) {
        result = null;
      } else if (_.includes(['array', 'range'], type)) {
        result = asArray(queryArg);
      } else if (type === 'boolean') {
        result = lenientBoolean(queryArg);
      } else {
        result = queryArg;
      }
      return result;
    };

    /**
     * Filters of type 'range' have only one 'subcategory.value' and it's an array. The first and last
     * elements in the array determine the range 'start' and 'stop'.
     *
     * @param  {Object}     filterDefinitions    Including, or example, definition of the 'majors' filter option.
     * @param  {Object}     addedFilters         Filters added, by user, to search criteria.
     * @return {Object}                          Data structure compatible with cohort_filters db table.
     */
    var toFilterCriteria = function(filterDefinitions, addedFilters) {
      var filterCriteria = {};

      _.each(filterDefinitions, function(d) {
        if (d !== null) {
          if (!_.isNil(d.defaultValue)) {
            // Eg, default value of 'isInactiveAsc' varies per user
            filterCriteria[d.key] = d.defaultValue;
          }
          var values = [];
          _.each(addedFilters, function(filter) {
            if (d.key === filter.key) {
              if (filter.type === 'boolean') {
                values.push(filter.value);
              } else if (filter.type === 'array') {
                values.push(filter.subcategory.value);
              } else if (filter.type === 'range') {
                values = values.concat(filter.subcategory.value);
              }
            }
          });
          if (values.length) {
            filterCriteria[d.key] = translateQueryArg(d, values);
          }
        }
      });
      return filterCriteria;
    };

    var getRangeDisplayName = function(start, stop) {
      return start === stop ? 'Starts with ' + start : start + ' through ' + stop;
    };

    /**
     * Transform Cohort's existing filter-criteria are converted to an array of arrays. For example, if criteria has
     * majors: [a, b, c] then this function will prepare three rows.
     *
     * The value of the subcategory dropdown-select is always an array with a single string. For example,
     * the 'Levels' filter has subcategory dropdown-select with four options but user can only choose one so
     * 'subcategoryOption' below is an array of length == 1.
     *
     * @param  {Object}     filterCriteria    Has filter-criteria of saved search.
     * @param  {Object}     filterDefinitions An array including, for example, the 'majors' filter definition.
     * @param  {Function}   callback          Standard callback
     * @return {Object}                       Bundle with criteria-reference object and selected cohort filter criteria.
     */
    var initFiltersForDisplay = function(filterCriteria, filterDefinitions, callback) {
      var addedFilters = [];

      _.each(filterCriteria, function(selectedOptions, key) {
        if (lenientBoolean(selectedOptions)) {
          var d = _.find(filterDefinitions, ['key', key]);
          var values = translateQueryArg(d, selectedOptions);
          values = Array.isArray(values) ? values : [ values ];
          if (d.type === 'range') {
            values.sort();
            var start = values[0];
            var stop = _.last(values);
            addedFilters.push({
              key: d.key,
              name: d.name,
              type: d.type,
              subcategory: {
                name: getRangeDisplayName(start, stop),
                value: [start, stop]
              }
            });
            d.disabled = true;

          } else {
            _.each(values, function(value) {
              if (value) {
                var addedFilter = {
                  key: d.key,
                  name: d.name,
                  type: d.type,
                  value: value
                };
                if (d.type === 'array') {
                  var subcategory = _.find(d.options, ['value', value]);
                  if (subcategory) {
                    addedFilter.subcategory = _.pick(subcategory, [
                      'key',
                      'name',
                      'position',
                      'value'
                    ]);
                    subcategory.disabled = true;
                    var remainingAvailable = _.omitBy(d.options, 'disabled');
                    d.disabled = _.isEmpty(remainingAvailable);
                  }
                } else {
                  d.disabled = true;
                }
                addedFilters.push(addedFilter);
              }
            });
          }
        }
      });
      return callback(sortAddedFilters(filterDefinitions, addedFilters));
    };

    return {
      getRangeDisplayName: getRangeDisplayName,
      initFiltersForDisplay: initFiltersForDisplay,
      sortAddedFilters: sortAddedFilters,
      toFilterCriteria: toFilterCriteria,
      translateQueryArg: translateQueryArg
    };
  });

}(window.angular));
