(function(angular) {

  angular.module('boac', ['ngRoute']);

  var bootstrap = function() {
    angular.element(document).ready(function() {
      angular.bootstrap(document, [ 'boac' ]);
    });
  };

  bootstrap();

}(window.angular));
