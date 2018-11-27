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

  boac.factory('studentFactory', function($http, utilService) {

    var analyticsPerStudent = function(uid) {
      return $http.get('/api/student/' + uid + '/analytics');
    };

    var dismissAlert = function(alertId) {
      return $http.get('/api/alerts/' + alertId + '/dismiss');
    };

    var getAlerts = function(sid) {
      return $http.get('/api/alerts/current/' + sid);
    };

    var getRelevantMajors = function() {
      return $http.get('/api/majors/relevant');
    };

    var getStudents = function(criteria, orderBy, offset, limit) {
      var args = _.merge({
        orderBy: orderBy || 'first_name',
        offset: offset || 0,
        limit: limit || 50
      }, criteria);
      return $http.post('/api/students', args);
    };

    var getAllTeamGroups = function() {
      return $http.get('/api/team_groups/all');
    };

    var searchForStudents = function(searchPhrase, includeCourses, isInactiveAsc, orderBy, offset, limit) {
      var args = {
        searchPhrase: searchPhrase,
        includeCourses: includeCourses,
        isInactiveAsc: utilService.toBoolOrNull(isInactiveAsc),
        orderBy: orderBy || 'first_name',
        offset: offset || 0,
        limit: limit || 50
      };
      return $http.post('/api/students/search', args);
    };

    return {
      analyticsPerStudent: analyticsPerStudent,
      dismissAlert: dismissAlert,
      getAlerts: getAlerts,
      getRelevantMajors: getRelevantMajors,
      getStudents: getStudents,
      getAllTeamGroups: getAllTeamGroups,
      searchForStudents: searchForStudents
    };
  });

}(window.angular));
