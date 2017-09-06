(function(angular) {

	'use strict';

	angular.module('boac').config(function($locationProvider, $routeProvider) {
		$routeProvider
			.otherwise({
				redirectTo: '/'
			});

		$locationProvider.html5Mode(true);
	});

}(window.angular));
