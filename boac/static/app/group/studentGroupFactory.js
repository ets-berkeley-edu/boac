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

    var addStudentsToGroup = function(groupId, students) {
      var args = {
        groupId: groupId,
        sids: _.map(students, 'sid')
      };
      return $http.post('/api/group/students/add', args).then(function() {
        _.each(students, function(student) {
          $rootScope.$broadcast('addStudentToGroup', {groupId: groupId, student: student});
        });
      });
    };

    var addStudentToGroup = function(groupId, student) {
      return $http.get('/api/group/' + groupId + '/add_student/' + student.sid).then(function() {
        $rootScope.$broadcast('addStudentToGroup', {groupId: groupId, student: student});
      });
    };

    var createGroup = function(name) {
      return $http.post('/api/group/create', {name: name}).then(function(response) {
        $rootScope.$broadcast('groupCreated', {group: response.data});
      });
    };

    var deleteGroup = function(id) {
      return $http.delete('/api/group/delete/' + id).then(function() {
        $rootScope.$broadcast('groupDeleted', {groupId: id});
      });
    };

    var getMyGroups = function() {
      return $http.get('/api/groups/my');
    };

    var getGroup = function(id) {
      return $http.get('/api/group/' + id);
    };

    var getMyPrimaryGroup = function() {
      return $http.get('/api/group/my_primary');
    };

    var removeStudentFromGroup = function(groupId, student) {
      return $http.delete('/api/group/' + groupId + '/remove_student/' + student.sid).then(function() {
        $rootScope.$broadcast('removeStudentFromGroup', {groupId: groupId, student: student});
      });
    };

    var changeGroupName = function(groupId, name) {
      return $http.post('/api/group/update', {id: groupId, name: name}).then(function(response) {
        $rootScope.$broadcast('groupNameChanged', {group: response.data});
      });
    };

    return {
      addStudentsToGroup: addStudentsToGroup,
      addStudentToGroup: addStudentToGroup,
      changeGroupName: changeGroupName,
      createGroup: createGroup,
      deleteGroup: deleteGroup,
      getGroup: getGroup,
      getMyGroups: getMyGroups,
      getMyPrimaryGroup: getMyPrimaryGroup,
      removeStudentFromGroup: removeStudentFromGroup
    };
  });

}(window.angular));
