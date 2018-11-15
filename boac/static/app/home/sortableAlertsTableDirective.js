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

  angular.module('boac').directive('sortableAlertsTable', function(authService, config) {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {
        options: '=',
        students: '='
      },

      templateUrl: '/static/app/home/sortableAlertsTable.html',

      link: function(scope) {
        scope.isAscUser = authService.isAscUser();
        scope.demoMode = config.demoMode;
        scope.abbreviateTermName = function(termName) {
          return termName && termName.replace('20', ' \'').replace('Spring', 'Spr').replace('Summer', 'Sum');
        };

        scope.srText = {
          sortableName: 'student name',
          sid: 'S I D',
          'majors[0]': 'major',
          'expectedGraduationTerm.id': 'expected graduation term',
          'term.enrolledUnits': 'term units',
          cumulativeUnits: 'units completed',
          cumulativeGPA: 'GPA',
          alertCount: 'issue count'
        };

        var setSortDescriptions = function() {
          scope.sortOptions = {};
          scope.currentSortDescription = 'Sorted by ' + scope.srText[scope.options.sortBy];
          if (scope.options.reverse) {
            scope.currentSortDescription += ' descending';
          }
          scope.sortOptions = _.mapValues(scope.srText, function(value, key) {
            var optionText = 'Sort by ' + value;
            if (key === scope.options.sortBy) {
              optionText += scope.options.reverse ? ' ascending' : ' descending';
            }
            return optionText;
          });
        };
        setSortDescriptions();

        scope.sort = function(options, sortBy) {
          if (options.sortBy === sortBy) {
            options.reverse = !options.reverse;
          } else {
            options.sortBy = sortBy;
            options.reverse = false;
          }
          scope.resorted = true;
          setSortDescriptions();
        };
      }
    };
  });

}(window.angular));
