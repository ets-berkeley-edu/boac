(function(angular) {

  'use strict';

  angular.module('boac').config(function($locationProvider, $stateProvider, $urlRouterProvider) {

    // Use the HTML5 location provider to ensure that the $location service getters
    // and setters interact with the browser URL address through the HTML5 history API
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
        url: '/cohort/:code',
        templateUrl: '/static/app/cohort/cohort.html',
        controller: 'CohortController'
      })
      .state('manageCohorts', {
        url: '/cohorts/manage',
        templateUrl: '/static/app/cohort/manage.html',
        controller: 'ManageCohortsController'
      })
      .state('user', {
        url: '/student/:uid',
        templateUrl: '/static/app/student/student.html',
        controller: 'StudentController'
      })
      .state('search', {
        url: '/search',
        templateUrl: '/static/app/student/search.html',
        controller: 'SearchController'
      });
  });

}(window.angular));
