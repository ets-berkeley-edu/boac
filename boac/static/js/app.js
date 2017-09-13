(function(angular) {

  var boac = angular.module('boac', [ 'ngRoute' ]);

  var loadConstants = function() {
    var initInjector = angular.injector([ 'ng' ]);
    var $http = initInjector.get('$http');
    var $q = initInjector.get('$q');

    return $q.all({
      status: $http.get('/api/status'),
      config: $http.get('/api/config')
    }).then(function(results) {
      boac.value('me', results.status.data);
      boac.constant('config', results.config.data);
    });
  };

  var bootstrap = function() {
    angular.element(document).ready(function() {
      angular.bootstrap(document, [ 'boac' ]);
    });
  };

  loadConstants().then(bootstrap);

}(window.angular));
