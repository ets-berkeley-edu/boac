/**
 * Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.
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

  angular.module('boac').service('utilService', function($sce, authService, config) {

    var disableMatrixViewThreshold = parseInt(config.disableMatrixViewThreshold, 10);
    var exceedsMatrixThresholdMessage = 'Sorry, the matrix view is only available when total student count is below ' + disableMatrixViewThreshold + '. Please narrow your search.';

    var toBoolOrNull = function(str) {
      return _.isNil(str) ? null : _.lowerCase(str) === 'true';
    };

    var displayAsInactive = function(student) {
      return (authService.isAscUser() && !student.athleticsProfile.isActiveAsc) || (authService.isCoeUser() && !student.coeProfile.isActiveCoe);
    };

    var exceedsMatrixThreshold = function(studentCount) {
      return parseInt(studentCount, 10) > disableMatrixViewThreshold;
    };

    var lastActivityDays = function(analytics) {
      var timestamp = parseInt(_.get(analytics, 'lastActivity.student.raw'), 10);
      if (!timestamp || isNaN(timestamp)) {
        return 'Never';
      }
      // Days tick over at midnight according to the user's browser.
      var daysSince = Math.round(((new Date()).setHours(0, 0, 0, 0) - (new Date(timestamp * 1000)).setHours(0, 0, 0, 0)) / 86400000);
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

    var previousSisTermId = function(termId) {
      var previousTermId = '';
      var strTermId = termId.toString();
      switch (strTermId.slice(3)) {
        case '2':
          previousTermId = (parseInt(strTermId.slice(0, 3), 10) - 1).toString() + '8';
          break;
        case '5':
          previousTermId = strTermId.slice(0, 3) + '2';
          break;
        case '8':
          previousTermId = strTermId.slice(0, 3) + '5';
          break;
        default:
          break;
      }
      return previousTermId;
    };

    var termNameForSisId = function(termId) {
      var strTermId = termId.toString();
      var termName = '20' + strTermId.slice(1, 3);
      switch (strTermId.slice(3)) {
        case '2':
          termName = 'Spring ' + termName;
          break;
        case '5':
          termName = 'Summer ' + termName;
          break;
        case '8':
          termName = 'Fall ' + termName;
          break;
        default:
          break;
      }
      return termName;
    };

    var uibPopoverError = function(errorMessage) {
      return {
        popoverHtml: $sce.trustAsHtml('<i class="fas fa-exclamation-triangle"></i> ' + errorMessage),
        isPopoverOpen: true
      };
    };

    return {
      displayAsInactive: displayAsInactive,
      exceedsMatrixThreshold: exceedsMatrixThreshold,
      exceedsMatrixThresholdMessage: exceedsMatrixThresholdMessage,
      extendSortableNames: extendSortableNames,
      lastActivityDays: lastActivityDays,
      lastActivityInContext: lastActivityInContext,
      previousSisTermId: previousSisTermId,
      termNameForSisId: termNameForSisId,
      toBoolOrNull: toBoolOrNull,
      uibPopoverError: uibPopoverError
    };
  });

}(window.angular));
