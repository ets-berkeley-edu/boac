(function(angular) {
  'use strict';

  angular.module('boac').config(function($locationProvider, $routeProvider) {
    $routeProvider.when('/', {
      templateUrl: 'static/templates/landing.html',
      controller: 'LandingController'
    }).otherwise({
      redirectTo: '/'
    });

    $locationProvider.html5Mode(true);
  });

}(window.angular));
