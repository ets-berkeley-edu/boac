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

  angular.module('boac').factory('authFactory', function($http, $rootScope, $state) {

    var loadUserProfile = function(results) {
      // Refresh instance currently referenced in templates
      var me = results.data;
      $rootScope.me = me;
      $rootScope.$broadcast('userStatusChange');
      // Load user profile if authenticated
      if (me.authenticated_as.is_authenticated) {
        return $http.get('/api/profile').then(function(profileResults) {
          _.extend($rootScope.me, profileResults.data);
        });
      }
      return results;
    };

    var casLogIn = function() {
      return $http.get('/cas/login_url').then(function(results) {
        window.location = results.data.cas_login_url;
      });
    };

    var devAuthLogIn = function(uid, password) {
      var credentials = {
        uid: uid,
        password: password
      };
      return $http.post('/devauth/login', credentials).then(
        function successCallback() {
          $state.go('home', {}, {reload: true});
        },
        function errorCallback() {
          $rootScope.$broadcast('devAuthFailure');
          $rootScope.me = null;
        });
    };

    var logOut = function() {
      return $http.get('/logout').then(function(results) {
        window.location = results.data.cas_logout_url;
      });
    };

    return {
      casLogIn: casLogIn,
      devAuthLogIn: devAuthLogIn,
      loadUserProfile: loadUserProfile,
      logOut: logOut
    };
  });

}(window.angular));
