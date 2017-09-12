(function(angular) {

  var boac = angular.module('boac', [ 'ngRoute' ]);

  var loadConstants = function() {
    var initInjector = angular.injector([ 'ng' ]);
    var $http = initInjector.get('$http');

    return $http.get('/api/status').then(function(results) {
      boac.value('me', results.data);
    });
  };

  var bootstrap = function() {
    angular.element(document).ready(function() {
      angular.bootstrap(document, [ 'boac' ]);
    });
  };

  loadConstants().then(bootstrap);

}(window.angular));
