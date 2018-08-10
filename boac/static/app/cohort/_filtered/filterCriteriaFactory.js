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
    var filterDefinitions = function() {
      var ref = [
        {
          available: authService.canViewCoe(),
          defaultValue: [],
          depth: 2,
          key: 'advisorLdapUid',
          name: 'Advisor',
          handler: utilService.asArray,
          param: 'a'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          key: 'gpaRanges',
          handler: utilService.asArray,
          name: 'GPA',
          param: 'g'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: [],
          depth: 2,
          key: 'groupCodes',
          handler: utilService.asArray,
          name: 'Teams',
          param: 't'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: false,
          depth: 1,
          handler: utilService.lenientBoolean,
          key: 'isInactiveAsc',
          name: 'Inactive',
          param: 'v'
        },
        {
          available: authService.canViewAsc(),
          defaultValue: false,
          depth: 1,
          handler: utilService.lenientBoolean,
          key: 'inIntensiveCohort',
          name: 'Intensive',
          param: 'i'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'levels',
          name: 'Levels',
          param: 'l'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'majors',
          name: 'Majors',
          param: 'm'
        },
        {
          available: true,
          defaultValue: [],
          depth: 2,
          handler: utilService.asArray,
          key: 'unitRanges',
          name: 'Units',
          param: 'u'
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
        'groupCodes',
        'isInactiveAsc',
        'inIntensiveCohort'
      ];
    };

    return {
      filterDefinitions: filterDefinitions,
      getPrimaryFilterSortOrder: getPrimaryFilterSortOrder
    };

  });

}(window.angular));
