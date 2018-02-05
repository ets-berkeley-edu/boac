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
      .state('landing', {
        url: '/',
        templateUrl: '/static/app/landing/landing.html',
        controller: 'LandingController',
        resolve: resolvePublic
      })
      .state('cohort', {
        url: '/cohort?c&i&inactive',
        templateUrl: '/static/app/cohort/cohort.html',
        controller: 'CohortController',
        resolve: resolvePrivate,
        reloadOnSearch: false
      })
      .state('allCohorts', {
        url: '/cohorts/all',
        templateUrl: '/static/app/cohort/all.html',
        controller: 'AllCohortsController',
        resolve: resolvePrivate
      })
      .state('manageCohorts', {
        url: '/cohorts/manage',
        templateUrl: '/static/app/cohort/manageCohorts.html',
        controller: 'ManageCohortsController',
        resolve: resolvePrivate
      })
      .state('user', {
        url: '/student/:uid?r',
        templateUrl: '/static/app/student/student.html',
        controller: 'StudentController',
        resolve: resolvePrivate,
        reloadOnSearch: false
      });

  }).run(function($rootScope, $state) {
    $rootScope.$on('$stateChangeError', function(event, toState, toParams, fromState, fromParams, error) {
      if (error.message === 'unauthenticated') {
        $state.go('landing', {}, {reload: true});
      }
    });
  });

}(window.angular));
