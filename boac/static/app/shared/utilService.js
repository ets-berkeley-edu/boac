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

    var decorateOrderedSet = function(set) {
      return _.map(set, function(obj, index) {
        return obj && _.merge(obj, {position: index});
      });
    };

    var lastActivityDays = function(analytics) {
      var timestamp = parseInt(_.get(analytics, 'lastActivity.student.raw'), 10);
      if (!timestamp || isNaN(timestamp)) {
        return 'Never';
      }
      var daysSince = Math.floor(((Date.now() / 1000) - timestamp) / 86400);
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

    var lenientBoolean = function(obj) {
      var value = asArray(obj);
      return !_.isEmpty(value) && _.lowerCase(value[0]) !== 'false';
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
      decorateOrderedSet: decorateOrderedSet,
      exceedsMatrixThreshold: exceedsMatrixThreshold,
      exceedsMatrixThresholdMessage: exceedsMatrixThresholdMessage,
      extendSortableNames: extendSortableNames,
      format: format,
      lastActivityDays: lastActivityDays,
      lastActivityInContext: lastActivityInContext,
      lenientBoolean: lenientBoolean,
      toBoolOrNull: toBoolOrNull
    };
  });

}(window.angular));
