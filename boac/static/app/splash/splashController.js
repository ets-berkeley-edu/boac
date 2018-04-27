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

  angular.module('boac').controller('SplashController', function(
    authFactory,
    config,
    validationService,
    $location,
    $rootScope,
    $sce,
    $scope,
    $stateParams
  ) {

    $rootScope.pageTitle = 'Welcome';

    var closeErrorPopovers = $scope.closeErrorPopovers = function() {
      _.set($scope.casLogin, 'error.isPopoverOpen', false);
      _.set($scope.devAuth, 'error.isPopoverOpen', false);
    };

    var uibPopoverError = function(errorMessage) {
      return {
        popoverHtml: $sce.trustAsHtml('<i class="fas fa-exclamation-triangle"></i> ' + errorMessage),
        isPopoverOpen: true
      };
    };

    $scope.signIn = function() {
      closeErrorPopovers();
      authFactory.casLogIn().then(
        function success(results) {
          window.location = results.data.cas_login_url;
        },
        function failure(err) {
          var errorMessage = validationService.parseError(err);
          $scope.casLogin = {error: uibPopoverError(errorMessage)};
        }
      );
    };

    var init = function() {
      var casLoginError = _.get($location.search(), 'casLoginError') || $stateParams.casLoginError;
      if (casLoginError) {
        $scope.casLogin = {error: uibPopoverError(casLoginError)};
      }
      if (config.devAuthEnabled) {
        $scope.devAuthLogIn = function(uid, password) {
          closeErrorPopovers();
          return authFactory.devAuthLogIn(uid, password).then(
            function success() {
              window.location.replace('/home');
            },
            function failure(err) {
              var errorMessage = validationService.parseError(err).message;
              $scope.devAuth = {error: uibPopoverError(errorMessage)};
            }
          );
        };
      }
    };

    init();
  });

}(window.angular));
