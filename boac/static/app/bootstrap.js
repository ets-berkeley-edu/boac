(function(angular) {

  var boac = angular.module('boac', [
    'base64',
    'oi.select',
    'ui.bootstrap',
    'ui.router'
  ]);

  var loadConstants = function() {
    var initInjector = angular.injector([ 'ng' ]);
    var $http = initInjector.get('$http');

    return $http.get('/api/config').then(function(results) {
      boac.constant('config', results.data);
    });
  };

  var bootstrap = function() {
    angular.element(document).ready(function() {
      angular.bootstrap(document, [ 'boac' ]);
    });
  };

  loadConstants().then(bootstrap);

}(window.angular));
