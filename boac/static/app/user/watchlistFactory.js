(function(angular) {

  'use strict';

  var boac = angular.module('boac');

  boac.factory('watchlistFactory', function(googleAnalyticsService, utilService, $http, $rootScope) {

    var getMyWatchlist = function() {
      return $http.get('/api/watchlist/my');
    };

    var addToWatchlist = function(sid) {
      return $http.get('/api/watchlist/add/' + sid).then(function() {
        $rootScope.$broadcast('watchlistAddition', sid);
      });
    };

    var removeFromWatchlist = function(sid) {
      return $http.get('/api/watchlist/remove/' + sid).then(function() {
        $rootScope.$broadcast('watchlistRemoval', sid);
      });
    };

    return {
      addToWatchlist: addToWatchlist,
      getMyWatchlist: getMyWatchlist,
      removeFromWatchlist: removeFromWatchlist
    };
  });

}(window.angular));
