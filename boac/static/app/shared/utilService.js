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

  angular.module('boac').service('utilService', function(config) {

    var disableMatrixViewThreshold = parseInt(config.disableMatrixViewThreshold, 10);
    var exceedsMatrixThresholdMessage = 'Sorry, the matrix view is only available when total student count is below ' + disableMatrixViewThreshold + '. Please narrow your search.';

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

    var toBoolOrNull = function(str) {
      return _.isNil(str) ? null : _.lowerCase(str) === 'true';
    };

    var exceedsMatrixThreshold = function(studentCount) {
      return parseInt(studentCount, 10) > disableMatrixViewThreshold;
    };

    var format = function(str, tokens) {
      var formatted = str;
      _.each(tokens, function(value, key) {
        formatted = formatted.replace('${' + key + '}', value);
      });
      return formatted;
    };

    /**
     * Standard set of menu options per expectations of cohort-view, etc.
     *
     * @param  {Array}    options      Set of menu options
     * @param  {String}   pkRef        Key used to get primary-key of each option in options
     * @return {Array}                 Enhanced set of menu options (eg, unique 'id' property per option)
     */
    var decorateOptions = function(options, pkRef) {
      return _.map(options, function(option) {
        if (option && option[pkRef]) {
          option.name = option.name || option[pkRef];
          option.value = option.value || option[pkRef];
          option.id = option.id || _.toLower(option.name.replace(/\W+/g, '-'));
        }
        return option;
      });
    };

    /**
     * Extract 'value' property of each selected option in options array.
     *
     * @param  {Array}    options      Set of menu options
     * @param  {String}   [valueRef]   Optional key used to lookup value of menu option. Default key is 'value'.
     * @return {Array}                 Values (strings) of selected options
     */
    var getValuesSelected = function(options, valueRef) {
      return _.map(_.filter(options, 'selected'), valueRef || 'value');
    };

    /**
     * @param  {String}     str      Word/phrase with camelCase
     * @return {String}              All 'camelCase' are converted to 'camel-case'
     */
    var camelCaseToDashes = function(str) {
      return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
    };

    var lastActivityDays = function(analytics) {
      var daysSince = parseInt(_.get(analytics, 'lastActivity.student.daysSinceLastActivity'), 10);
      if (isNaN(daysSince)) {
        return 'Never';
      }
      switch (daysSince) {
        case 0: return 'Today';
        case 1: return 'Yesterday';
        default: return daysSince + ' days ago';
      }
    };

    var lastActivityInContext = function(analytics) {
      var describe = '';
      if (analytics.courseEnrollmentCount) {
        var total = analytics.courseEnrollmentCount;
        var percentAbove = (100 - analytics.lastActivity.student.roundedUpPercentile) / 100;
        describe += Math.round(percentAbove * total) + ' out of ' + total + ' enrolled students have done so more recently.';
      }
      return describe;
    };

    var extendSortableNames = function(students) {
      return _.map(students, function(student) {
        return _.extend(student, {
          sortableName: student.lastName + ', ' + student.firstName
        });
      });
    };

    return {
      asArray: asArray,
      camelCaseToDashes: camelCaseToDashes,
      exceedsMatrixThreshold: exceedsMatrixThreshold,
      exceedsMatrixThresholdMessage: exceedsMatrixThresholdMessage,
      lastActivityDays: lastActivityDays,
      lastActivityInContext: lastActivityInContext,
      extendSortableNames: extendSortableNames,
      decorateOptions: decorateOptions,
      format: format,
      getValuesSelected: getValuesSelected,
      toBoolOrNull: toBoolOrNull
    };
  });

}(window.angular));
