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

  angular.module('boac').controller('ManageGroupsController', function(
    authService,
    studentGroupFactory,
    studentGroupService,
    validationService,
    $rootScope,
    $scope
  ) {

    $scope.isLoading = true;
    $scope.isMyPrimaryGroup = studentGroupService.isMyPrimaryGroup;

    var resetPageView = function(callback) {
      _.each($scope.myGroups, function(group) {
        group.editMode = false;
      });
      return callback();
    };

    var setEditMode = $scope.setEditMode = function(group, newValue) {
      resetPageView(function() {
        group.editMode = newValue;
      });
    };

    $scope.cancelEdit = function(group) {
      group.name = group.nameOriginal;
      setEditMode(group, false);
    };

    $scope.changeGroupName = function(group, name) {
      validationService.validateName({id: group.id, name: name}, authService.getMe().myGroups, function(error) {
        group.error = error;
        group.hideError = false;
        if (!group.error) {
          studentGroupFactory.changeGroupName(group.id, name).then(function() {
            group.nameOriginal = name;
            setEditMode(group, false);
          });
        }
      });
    };

    /**
     * @return {void}
     */
    var init = function() {
      studentGroupFactory.getMyGroups().then(function(response) {
        $scope.myGroups = response.data;
        _.each($scope.myGroups, function(group) {
          group.nameOriginal = group.name;
        });
        resetPageView(angular.noop);
        $scope.isLoading = false;
      });
    };

    $rootScope.$on('groupCreated', function(event, data) {
      $scope.myGroups.push(data.group);
    });

    $rootScope.$on('groupDeleted', function(event, data) {
      $scope.myGroups = _.remove($scope.myGroups, function(group) {
        return group.id !== data.groupId;
      });
    });

    init();
  });

}(window.angular));
