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

  angular.module('boac').service('filterCriteriaFactory', function(authService, utilService) {

    /**
     * @return {Array}    List of cohort filter-criteria, available to current user, with defining attributes.
     */
    var getFilterDefinitions = function() {
      var ref = [
        {
          available: authService.canViewCoe(),
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'advisorLdapUids',
          name: 'Advisor',
          param: 'advisor',
          subcategoryHeader: 'Advisor'
        },
        {
          available: authService.canViewCoe(),
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'ethnicities',
          name: 'Ethnicities',
          param: 'ethnicity',
          subcategoryHeader: 'Ethnicity'
        },
        {
          available: authService.canViewCoe(),
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'genders',
          name: 'Genders',
          param: 'gender',
          subcategoryHeader: 'Gender'
        },
        {
          available: true,
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'gpaRanges',
          name: 'GPA',
          param: 'gpa',
          subcategoryHeader: 'GPA Range'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'groupCodes',
          name: 'Teams',
          param: 'team',
          subcategoryHeader: 'Team'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: (authService.isAscUser() ? false : null),
          handler: utilService.lenientBoolean,
          depth: 1,
          key: 'isInactiveAsc',
          name: 'Inactive',
          param: 'inactive'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: null,
          depth: 1,
          handler: utilService.lenientBoolean,
          key: 'inIntensiveCohort',
          name: 'Intensive',
          param: 'intensive'
        },
        {
          available: true,
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'levels',
          name: 'Levels',
          param: 'level',
          subcategoryHeader: 'Level'
        },
        {
          available: true,
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'majors',
          name: 'Majors',
          param: 'major',
          subcategoryHeader: 'Major'
        },
        {
          available: authService.canViewCoe(),
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'coePrepStatuses',
          name: 'PREP',
          param: 'prep',
          subcategoryHeader: 'Status'
        },
        {
          available: true,
          defaultValue: null,
          depth: 2,
          handler: utilService.asArray,
          key: 'unitRanges',
          name: 'Units',
          param: 'units',
          subcategoryHeader: 'Unit Range'
        }
      ];
      // Remove filters based on auth rules; see 'available' property above.
      return _.filter(_.clone(ref), 'available');
    };

    var getPrimaryFilterSortOrder = function() {
      return [
        'gpaRanges',
        null,
        'levels',
        'unitRanges',
        'majors',
        null,
        'advisorLdapUids',
        'ethnicities',
        'genders',
        'groupCodes',
        'isInactiveAsc',
        'inIntensiveCohort',
        'coePrepStatuses'
      ];
    };

    return {
      getFilterDefinitions: getFilterDefinitions,
      getPrimaryFilterSortOrder: getPrimaryFilterSortOrder
    };

  });

}(window.angular));
