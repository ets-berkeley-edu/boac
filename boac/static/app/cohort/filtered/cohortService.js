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

  angular.module('boac').service('cohortService', function(authService) {

    var getSearchPageTitle = function(criteria) {
      var definedKeys = _.keys(_.omitBy(criteria, _.isNil));
      var title = null;
      if (_.size(definedKeys) === 1) {
        var key = definedKeys[0];
        title = {
          inactive: 'Inactive',
          intensive: 'Intensive'
        }[key];
      }
      return title;
    };

    var getSortByOptionsForSearch = function() {
      var canViewAsc = authService.canViewAsc();
      var options = [
        {name: 'First Name', value: 'first_name', available: true},
        {name: 'Last Name', value: 'last_name', available: true},
        {name: 'GPA', value: 'gpa', available: true},
        {name: 'Level', value: 'level', available: true},
        {name: 'Major', value: 'major', available: true},
        {name: 'Team', value: 'group_name', available: canViewAsc},
        {name: 'Units Completed', value: 'units', available: true}
      ];

      return {
        options: _.filter(options, 'available'),
        selected: 'last_name'
      };
    };

    return {
      getSearchPageTitle: getSearchPageTitle,
      getSortByOptionsForSearch: getSortByOptionsForSearch
    };

  });
}(window.angular));
