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

    // Return a rejection if authenticated user is present.
    var splashAuthentication = function(me, $q) {
      var deferred = $q.defer();
      if (me.is_authenticated) {
        deferred.reject({message: 'authenticated'});
      } else {
        deferred.resolve({});
      }
      return deferred.promise;
    };

    var standardLayout = function(controller, templateUrl) {
      return {
        content: {
          controller: controller,
          templateUrl: templateUrl
        },
        footer: {templateUrl: '/static/app/nav/footer.html'},
        header: {
          controller: 'HeaderController',
          templateUrl: '/static/app/nav/header.html'
        },
        sidebar: {
          controller: 'SidebarNavController',
          templateUrl: '/static/app/nav/sidebar.html'
        }
      };
    };

    var resolveSplash = {
      me: resolveMe,
      authentication: splashAuthentication
    };

    var resolvePrivate = {
      me: resolveMe,
      authentication: resolveAuthentication
    };

    // Default route
    $urlRouterProvider.otherwise(function($injector, $location) {
      $injector.get('authService').reloadMe().then(function(me) {
        var uri = me && me.is_authenticated ? '/404' : '/';
        $location.replace().path(uri);
      });
    });

    // Routes
    $stateProvider
      .state('cohort', {
        url: '/cohort?c&i&inactive',
        views: standardLayout('CohortController', '/static/app/cohort/cohort.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('cohorts', {
        url: '/cohorts/all',
        views: standardLayout('AllCohortsController', '/static/app/cohort/all.html'),
        resolve: resolvePrivate
      })
      .state('cohortsManage', {
        url: '/cohorts/manage',
        views: standardLayout('ManageCohortsController', '/static/app/cohort/manageCohorts.html'),
        resolve: resolvePrivate
      })
      .state('teams', {
        url: '/cohorts/teams',
        views: standardLayout('TeamsController', '/static/app/cohort/teams.html'),
        resolve: resolvePrivate
      })
      .state('course', {
        url: '/course/:termId/:sectionId',
        views: standardLayout('CourseController', '/static/app/course/course.html'),
        resolve: resolvePrivate
      })
      .state('group', {
        url: '/group/:id',
        views: standardLayout('GroupController', '/static/app/group/group.html'),
        resolve: resolvePrivate
      })
      .state('groupsManage', {
        url: '/groups/manage',
        views: standardLayout('ManageGroupsController', '/static/app/group/manageGroups.html'),
        resolve: resolvePrivate
      })
      .state('home', {
        url: '/home',
        views: standardLayout('HomeController', '/static/app/home/home.html'),
        resolve: resolvePrivate
      })
      .state('splash', {
        url: '/',
        templateUrl: '/static/app/splash/splash.html',
        controller: 'SplashController',
        resolve: resolveSplash
      })
      .state('user', {
        url: '/student/:uid?r',
        views: standardLayout('StudentController', '/static/app/student/student.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      }).state('404', {
        url: '/404',
        views: standardLayout(null, '/static/app/shared/404.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      });

  }).run(function(authFactory, authService, $rootScope, $state) {
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
      } else if (error.message === 'authenticated') {
        $state.go('home');
      }
    });

    $rootScope.$on('$stateChangeSuccess', function(event, toState) {
      $rootScope.angularStateName = toState.name;
      document.body.scrollTop = document.documentElement.scrollTop = 0;
    });
  });

}(window.angular));
