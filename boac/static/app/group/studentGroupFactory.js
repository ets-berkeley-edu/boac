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

  boac.factory('studentGroupFactory', function(googleAnalyticsService, utilService, $http, $rootScope) {

    var addStudentToGroup = function(groupId, sid) {
      return $http.get('/api/group/' + groupId + '/add_student/' + sid).then(function() {
        $rootScope.$broadcast('addStudentToGroup', {groupId: groupId, sid: sid});
      });
    };

    var createStudentGroup = function(name) {
      return $http.post('/api/group/create', {name: name}).then(function(group) {
        $rootScope.$broadcast('studentGroupCreated', {group: group});
      });
    };

    var deleteStudentGroup = function(id) {
      return $http.delete('/api/group/delete/' + id).then(function() {
        $rootScope.$broadcast('studentGroupDeleted', {groupId: id});
      });
    };

    var getMyGroups = function() {
      return $http.get('/api/groups/my');
    };

    var getStudentGroup = function(id) {
      return $http.get('/api/group/' + id);
    };

    var getMyPrimaryGroup = function() {
      return $http.get('/api/group/my_primary');
    };

    var removeStudentFromGroup = function(groupId, sid) {
      return $http.delete('/api/group/' + groupId + '/remove_student/' + sid).then(function() {
        $rootScope.$broadcast('removeStudentFromGroup', {groupId: groupId, sid: sid});
      });
    };

    return {
      addStudentToGroup: addStudentToGroup,
      createStudentGroup: createStudentGroup,
      deleteStudentGroup: deleteStudentGroup,
      getMyGroups: getMyGroups,
      getStudentGroup: getStudentGroup,
      getMyPrimaryGroup: getMyPrimaryGroup,
      removeStudentFromGroup: removeStudentFromGroup
    };
  });

}(window.angular));
