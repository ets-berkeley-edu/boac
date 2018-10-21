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

  angular.module('boac').config(function($locationProvider, $stateProvider, $urlRouterProvider) {

    $locationProvider.html5Mode({
      enabled: true,
      requireBase: false
    });

    var authenticatedProfile = function($http, $injector, $q, $rootScope) {
      return $q(function(resolve, reject) {
        var status = $injector.get('status');

        if (_.get(status, 'isAuthenticated')) {
          if (_.get($rootScope, 'profile')) {
            resolve({message: 'authenticated'});
          } else {
            $http.get('/api/profile/my').then(function(response) {
              $rootScope.profile = response.data;
              $rootScope.$broadcast('userProfileLoaded', {
                profile: $rootScope.profile
              });
              resolve({message: 'authenticated'});
            });
          }
        } else {
          reject();
        }
      });
    };

    var authenticatedAdmin = function($injector, $q) {
      var status = $injector.get('status');
      return $q(function(resolve, reject) {
        if (_.get(status, 'isAuthenticated') && _.get(status, 'isAdmin')) {
          resolve();
        } else {
          reject({message: 'unauthorized'});
        }
      });
    };

    var resolveLogin = function($injector, $q) {
      var status = $injector.get('status');
      return $q(function(resolve, reject) {
        if (_.get(status, 'isAuthenticated')) {
          reject({message: 'authenticated'});
        } else {
          resolve();
        }
      });
    };

    var standardLayout = function(controller, templateUrl) {
      return {
        content: {
          controller: controller,
          templateUrl: templateUrl
        }
      };
    };

    var resolvePrivate = {
      authentication: authenticatedProfile
    };

    // Default route
    $urlRouterProvider.otherwise(function($injector) {
      var status = $injector.get('status');
      return status.isAuthenticated ? '/home' : '/login';
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
        resolve: {
          authentication: authenticatedAdmin
        }
      })
      .state('filteredCohort', {
        url: '/cohort/filtered?id&inactive&intensive&name',
        views: standardLayout('FilteredCohortController', '/static/app/cohort/filtered/cohort.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('filteredCohortsAll', {
        url: '/cohort/filtered/all',
        views: standardLayout('AllFilteredCohortsController', '/static/app/cohort/filtered/all.html'),
        resolve: resolvePrivate
      })
      .state('course', {
        url: '/course/:termId/:sectionId',
        views: standardLayout('CourseController', '/static/app/course/course.html'),
        resolve: resolvePrivate
      })
      .state('curatedCohort', {
        url: '/cohort/curated/:id',
        views: standardLayout('CuratedCohortController', '/static/app/cohort/curated/cohort.html'),
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
      .state('login', {
        url: '/login',
        views: {
          login: {
            controller: 'LoginController',
            templateUrl: '/static/app/splash/login.html'
          }
        },
        resolve: {
          authentication: resolveLogin
        }
      })
      .state('search', {
        url: '/search?q',
        views: standardLayout('SearchController', '/static/app/search/searchResults.html'),
        resolve: resolvePrivate
      })
      .state('teams', {
        url: '/teams',
        views: standardLayout('TeamsController', '/static/app/athletics/teams.html'),
        resolve: resolvePrivate
      })
      .state('user', {
        url: '/student/:uid?r',
        views: standardLayout('StudentController', '/static/app/student/student.html'),
        resolve: resolvePrivate,
        reloadOnSearch: false
      });

  }).run(function($rootScope, $state, $transitions, authFactory, status) {

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
        $state.go('login', {casLoginError: message});
      }
    });

    $transitions.onEnter({}, function($transition) {
      $rootScope.angularStateName = $transition.$to().name;
      if ($transition.$to().name) {
        var name = $transition.$to().name;
        switch (name) {
          case 'filteredCohort':
            $rootScope.pageTitle = 'Filtered Cohort';
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

    $transitions.onStart({}, function() {
      $rootScope.status = status;
    });

    $transitions.onSuccess({}, function() {
      document.body.scrollTop = document.documentElement.scrollTop = 0;
    });
  });

}(window.angular));
