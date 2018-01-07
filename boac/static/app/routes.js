(function(angular) {

  'use strict';

  angular.module('boac').config(function($locationProvider, $stateProvider, $urlRouterProvider) {

    /**
     * Use the HTML5 location provider to ensure that the $location service getters
     * and setters interact with the browser URL address through the HTML5 history API
     */
    $locationProvider.html5Mode({
      enabled: true,
      requireBase: false
    });

    // Default route
    $urlRouterProvider.otherwise('/');

    // Routes
    $stateProvider
      .state('landing', {
        url: '/',
        templateUrl: '/static/app/landing/landing.html',
        controller: 'LandingController',
        isPublic: true
      })
      .state('cohort', {
        url: '/cohort?c',
        templateUrl: '/static/app/cohort/cohort.html',
        controller: 'CohortController',
        reloadOnSearch: false
      })
      .state('allCohorts', {
        url: '/cohorts/all',
        templateUrl: '/static/app/cohort/all.html',
        controller: 'AllCohortsController'
      })
      .state('manageCohorts', {
        url: '/cohorts/manage',
        templateUrl: '/static/app/cohort/manageCohorts.html',
        controller: 'ManageCohortsController'
      })
      .state('user', {
        url: '/student/:uid?r',
        templateUrl: '/static/app/student/student.html',
        controller: 'StudentController',
        reloadOnSearch: false
      });
  });

}(window.angular));
