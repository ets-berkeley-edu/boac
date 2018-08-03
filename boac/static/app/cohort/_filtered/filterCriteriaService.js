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

  angular.module('boac').service('filterCriteriaService', function($location, utilService) {

    var asArray = function(obj) {
      if (_.isNil(obj)) {
        return null;
      }
      return Array.isArray(obj) ? obj : [ obj ];
    };

    var criteriaRef = [
      {
        filter: 'advisorLdapUid',
        param: 'a',
        handler: asArray
      },
      {
        filter: 'gpaRanges',
        param: 'g',
        handler: asArray
      },
      {
        filter: 'groupCodes',
        param: 't',
        handler: asArray
      },
      {
        filter: 'intensive',
        param: 'i',
        handler: utilService.toBoolOrNull
      },
      {
        filter: 'inactive',
        param: 'v',
        handler: utilService.toBoolOrNull
      },
      {
        filter: 'levels',
        param: 'l',
        handler: asArray
      },
      {
        filter: 'majors',
        param: 'm',
        handler: asArray
      },
      {
        filter: 'unitRanges',
        param: 'u',
        handler: asArray
      }
    ];

    var getCohortIdFromLocation = function() {
      return parseInt($location.search().c, 10);
    };

    var getCriteriaFromLocation = function() {
      var queryArgs = _.clone($location.search());
      var criteria = {};

      _.each(criteriaRef, function(c) {
        criteria[c.filter] = c.handler(queryArgs[c.param]);
      });
      return criteria;
    };

    var updateLocation = function(filterCriteria) {
      var updates = [];

      _.each(filterCriteria, function(value, filterName) {
        var ref = _.find(criteriaRef, ['filter', filterName]);
        if (ref && !_.isNil(value)) {
          updates.push({param: ref.param, value: value});
        }
      });
      // Clear browser location then update
      $location.url($location.path());
      _.each(updates, function(update) {
        $location.search(update.param, update.value);
      });
    };

    return {
      getCohortIdFromLocation: getCohortIdFromLocation,
      getCriteriaFromLocation: getCriteriaFromLocation,
      updateLocation: updateLocation
    };

  });
}(window.angular));
