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

  angular.module('boac').config(function($locationProvider, $qProvider, $stateProvider, $urlRouterProvider) {
    /**
     * Use the HTML5 location provider to ensure that the $location service getters
     * and setters interact with the browser URL address through the HTML5 history API
     */
    $locationProvider.html5Mode({
      enabled: true,
      requireBase: false
    });

    // Authentication dependency for all states, public and private; get current user if any.
    var resolveMe = function(authService, $q) {
      var deferred = $q.defer();
      authService.reloadMe().then(function(me) {
        deferred.resolve(me);
      });
      return deferred.promise;
    };

    // Authentication dependency for private states only; return a rejection if authenticated user not present.
    var resolveAuthentication = function(me, $q) {
      var deferred = $q.defer();
      if (me.is_authenticated) {
        deferred.resolve({});
      } else {
        deferred.reject({message: 'unauthenticated'});
      }
      return deferred.promise;
    };

    var resolvePublic = {
      me: resolveMe
    };

    var resolvePrivate = {
      me: resolveMe,
      authentication: resolveAuthentication
    };

    // Default route
    $urlRouterProvider.otherwise('/');

    // Routes
    $stateProvider
      .state('cohort', {
        url: '/cohort?c&i&inactive',
        templateUrl: '/static/app/cohort/cohort.html',
        controller: 'CohortController',
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('cohorts', {
        url: '/cohorts/all',
        templateUrl: '/static/app/cohort/all.html',
        controller: 'AllCohortsController',
        resolve: resolvePrivate
      })
      .state('cohortsManage', {
        url: '/cohorts/manage',
        templateUrl: '/static/app/cohort/manageCohorts.html',
        controller: 'ManageCohortsController',
        resolve: resolvePrivate
      })
      .state('course', {
        url: '/course/:termId/:sectionId',
        templateUrl: '/static/app/course/course.html',
        controller: 'CourseController',
        resolve: resolvePrivate
      })
      .state('home', {
        url: '/',
        templateUrl: '/static/app/landing/landing.html',
        controller: 'LandingController',
        resolve: resolvePublic
      })
      .state('user', {
        url: '/student/:uid?r',
        templateUrl: '/static/app/student/student.html',
        controller: 'StudentController',
        resolve: resolvePrivate,
        reloadOnSearch: false
      });

  }).run(function(authFactory, $rootScope) {
    $rootScope.$on('$stateChangeStart', function(e, toState) {
      if (toState && toState.name) {
        var name = toState.name.replace(/([A-Z])/g, ' $1');
        $rootScope.pageTitle = name.charAt(0).toUpperCase() + name.slice(1);
      } else {
        $rootScope.pageTitle = 'UC Berkeley';
      }
    });
    $rootScope.$on('$stateChangeError', function(event, toState, toParams, fromState, fromParams, error) {
      if (error.message === 'unauthenticated') {
        authFactory.casLogIn();
      }
    });
  });

}(window.angular));
