(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(landingFactory, $scope) {
    var getStatus = function() {
      landingFactory.getAppState().then(function(appState) {
        $scope.status = appState.data;
      });
    };

    getStatus();
  });

}(window.angular));
