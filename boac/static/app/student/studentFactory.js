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

  var boac = angular.module('boac');

  boac.factory('studentFactory', function(utilService, $http) {

    var analyticsPerUser = function(uid) {
      return $http.get('/api/user/' + uid + '/analytics');
    };

    var dismissAlert = function(alertId) {
      return $http.get('/api/alerts/' + alertId + '/dismiss');
    };

    var getAlerts = function(sid) {
      return $http.get('/api/alerts/current/' + sid);
    };

    var getGpaRanges = function() {
      return [
        {name: '3.50 - 4.00', value: 'numrange(3.5, 4, \'[]\')'},
        {name: '3.00 - 3.49', value: 'numrange(3, 3.5, \'[)\')'},
        {name: '2.50 - 2.99', value: 'numrange(2.5, 3, \'[)\')'},
        {name: '2.00 - 2.49', value: 'numrange(2, 2.5, \'[)\')'},
        {name: 'Below 2.0', value: 'numrange(0, 2, \'[)\')'}
      ];
    };

    var getRelevantMajors = function() {
      return $http.get('/api/majors/relevant');
    };

    var getStudentLevels = function() {
      return [
        {name: 'Freshman (0-29 Units)', value: 'Freshman'},
        {name: 'Sophomore (30-59 Units)', value: 'Sophomore'},
        {name: 'Junior (60-89 Units)', value: 'Junior'},
        {name: 'Senior (90+ Units)', value: 'Senior'}
      ];
    };

    var getUnitRanges = function() {
      return [
        {name: '0 - 29', value: 'numrange(0, 30, \'[)\')'},
        {name: '30 - 59', value: 'numrange(30, 60, \'[)\')'},
        {name: '60 - 89', value: 'numrange(60, 90, \'[)\')'},
        {name: '90 - 119', value: 'numrange(90, 120, \'[)\')'},
        {name: '120 +', value: 'numrange(120, NULL, \'[)\')'}
      ];
    };

    var getStudents = function(
      advisorLdapUid,
      gpaRanges,
      groupCodes,
      intensive,
      isInactiveAsc,
      levels,
      majors,
      unitRanges,
      orderBy,
      offset,
      limit
    ) {
      var args = {
        advisorLdapUid: advisorLdapUid,
        gpaRanges: gpaRanges || [],
        groupCodes: groupCodes || [],
        isInactiveAsc: utilService.toBoolOrNull(isInactiveAsc),
        levels: levels || [],
        majors: majors || [],
        unitRanges: unitRanges || [],
        orderBy: orderBy || 'first_name',
        offset: offset || 0,
        limit: limit || 50
      };
      if (utilService.toBoolOrNull(intensive)) {
        args.inIntensiveCohort = true;
      }
      return $http.post('/api/students', args);
    };

    var searchForStudents = function(searchPhrase, isInactiveAsc, orderBy, offset, limit) {
      var args = {
        searchPhrase: searchPhrase,
        isInactiveAsc: utilService.toBoolOrNull(isInactiveAsc),
        orderBy: orderBy || 'first_name',
        offset: offset || 0,
        limit: limit || 50
      };
      return $http.post('/api/students/search', args);
    };

    return {
      analyticsPerUser: analyticsPerUser,
      dismissAlert: dismissAlert,
      getAlerts: getAlerts,
      getGpaRanges: getGpaRanges,
      getRelevantMajors: getRelevantMajors,
      getStudentLevels: getStudentLevels,
      getStudents: getStudents,
      getUnitRanges: getUnitRanges,
      searchForStudents: searchForStudents
    };
  });

}(window.angular));
