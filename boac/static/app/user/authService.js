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

  angular.module('boac').service('authService', function(
    authFactory,
    googleAnalyticsService,
    studentGroupFactory,
    $http,
    $location,
    $rootScope
  ) {

    var getMe = function() {
      return _.cloneDeep($rootScope.me.authenticated_as);
    };

    var reloadMe = function() {
      return $http.get('/api/status').then(authFactory.loadUserProfile).then(function() {
        var me = $rootScope.me.authenticated_as;
        if (me.is_authenticated) {
          if ($location.search().casLogin) {
            // Track CAS login event
            googleAnalyticsService.track('user', 'login', me.uid, parseInt(me.uid, 10));
          }
        }
        return me;
      });
    };

    $rootScope.$on('groupCreated', function(event, data) {
      if (_.get($rootScope, 'me.authenticated_as.myGroups')) {
        $rootScope.me.authenticated_as.myGroups.push(data.group);
      }
    });

    $rootScope.$on('groupDeleted', function(event, data) {
      if (_.get($rootScope, 'me.authenticated_as.myGroups')) {
        $rootScope.me.authenticated_as.myGroups = _.remove($rootScope.me.authenticated_as.myGroups, function(group) {
          return data.groupId !== group.id;
        });
      }
    });

    $rootScope.$on('groupNameChanged', function(event, data) {
      if (_.get($rootScope, 'me.authenticated_as.myGroups')) {
        _.each($rootScope.me.authenticated_as.myGroups, function(group) {
          if (data.group.id === group.id) {
            group.name = data.group.name;
          }
        });
      }
    });

    return {
      getMe: getMe,
      reloadMe: reloadMe
    };
  });

}(window.angular));
