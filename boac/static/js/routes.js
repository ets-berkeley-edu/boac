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
        templateUrl: '/static/templates/landing.html',
        controller: 'LandingController'
      });
  });

}(window.angular));
