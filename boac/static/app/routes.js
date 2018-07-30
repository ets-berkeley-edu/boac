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
      if (me.isAuthenticated) {
        deferred.resolve({});
      } else {
        deferred.reject({message: 'unauthenticated'});
      }
      return deferred.promise;
    };

    var resolveAdminAuthentication = function(me, $q) {
      var deferred = $q.defer();
      if (me.isAuthenticated && me.isAdmin) {
        deferred.resolve({});
      } else {
        deferred.reject({message: 'unauthorized'});
      }
      return deferred.promise;
    };

    // Return a rejection if authenticated user is present.
    var splashAuthentication = function(me, $q) {
      var deferred = $q.defer();
      if (me.isAuthenticated) {
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

    var resolveAdmin = {
      me: resolveMe,
      authentication: resolveAdminAuthentication
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
        var uri = me && me.isAuthenticated ? '/404' : '/';
        $location.replace().path(uri);
      });
    });

    // Routes
    $stateProvider
      .state('404', {
        url: '/404',
        views: standardLayout(null, '/static/app/shared/404.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('admin', {
        url: '/admin',
        views: standardLayout('AdminController', '/static/app/admin/admin.html'),
        resolve: resolveAdmin
      })
      .state('_filteredCohort', {
        url: '/_cohort/filtered?c&i&inactive',
        views: standardLayout('_FilteredCohortController', '/static/app/cohort/filtered/_filteredCohort.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('filteredCohort', {
        url: '/cohort/filtered?c&i&inactive',
        views: standardLayout('FilteredCohortController', '/static/app/cohort/filtered/filteredCohort.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('filteredCohortsAll', {
        url: '/cohort/filtered/all',
        views: standardLayout('AllFilteredCohortsController', '/static/app/cohort/filtered/all.html'),
        resolve: resolvePrivate
      })
      .state('filteredCohortsManage', {
        url: '/cohort/filtered/manage',
        views: standardLayout('ManageFilteredCohortsController', '/static/app/cohort/filtered/manage.html'),
        resolve: resolvePrivate
      })
      .state('course', {
        url: '/course/:termId/:sectionId',
        views: standardLayout('CourseController', '/static/app/course/course.html'),
        resolve: resolvePrivate
      })
      .state('curatedCohort', {
        url: '/cohort/curated/:id',
        views: standardLayout('CuratedCohortController', '/static/app/cohort/curated/curatedCohort.html'),
        resolve: resolvePrivate
      })
      .state('curatedCohortsManage', {
        url: '/cohort/curated/manage',
        views: standardLayout('ManageCuratedCohortsController', '/static/app/cohort/curated/manage.html'),
        resolve: resolvePrivate
      })
      .state('home', {
        url: '/home',
        views: standardLayout('HomeController', '/static/app/home/home.html'),
        resolve: resolvePrivate
      })
      .state('search', {
        url: '/search?q',
        views: standardLayout('SearchController', '/static/app/search/searchResults.html'),
        resolve: resolvePrivate
      })
      .state('splash', {
        url: '/',
        templateUrl: '/static/app/splash/splash.html',
        controller: 'SplashController',
        params: {casLoginError: null},
        resolve: resolveSplash
      })
      .state('teams', {
        url: '/teams',
        views: standardLayout('TeamsController', '/static/app/cohort/teams.html'),
        resolve: resolvePrivate
      })
      .state('user', {
        url: '/student/:uid?r',
        views: standardLayout('StudentController', '/static/app/student/student.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      });

  }).run(function(authFactory, authService, $rootScope, $state, $transitions) {

    $state.defaultErrorHandler(function(error) {
      var message = _.get(error, 'detail.message');
      if (message === 'unauthenticated') {
        authFactory.casLogIn().then(
          function(results) {
            window.location = results.data.cas_login_url;
          },
          function(err) {
            $state.go('splash', {casLoginError: _.get(err, 'data.message') || 'An unexpected error occurred.'});
          }
        );
      } else if (message === 'authenticated') {
        $state.go('home');
      } else if (message === 'unauthorized') {
        $state.go('404');
      } else {
        $state.go('splash', {casLoginError: message});
      }
    });

    $transitions.onStart({}, function($transition) {
      if ($transition.$to().name) {
        var name = $transition.$to().name;
        switch (name) {
          case 'filteredCohort':
            $rootScope.pageTitle = 'Filtered Cohort';
            break;
          case 'filteredCohortsManage':
            $rootScope.pageTitle = 'Manage Filtered Cohorts';
            break;
          case 'curatedCohort':
            $rootScope.pageTitle = 'Curated Cohort';
            break;
          case 'curatedCohortsManage':
            $rootScope.pageTitle = 'Manage Curated Cohorts';
            break;
          default:
            name = name.replace(/([A-Z])/g, ' $1');
            $rootScope.pageTitle = name.charAt(0).toUpperCase() + name.slice(1);
        }
      } else {
        $rootScope.pageTitle = 'UC Berkeley';
      }
    });

    $transitions.onSuccess({}, function($transition) {
      $rootScope.angularStateName = $transition.$to().name;
      document.body.scrollTop = document.documentElement.scrollTop = 0;
    });
  });

}(window.angular));
