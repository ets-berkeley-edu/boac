(function(angular) {

  'use strict';

  angular.module('boac').directive('watchlistToggle', function(watchlistFactory, $rootScope) {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {
        sid: '=',
        watchlist: '='
      },

      templateUrl: '/static/app/user/watchlistToggle.html',

      link: function(scope, elem, attrs) {
        scope.faSize = attrs.faSize;
        scope.onWatchlist = !!_.find(scope.watchlist, ['sid', scope.sid]);

        var buttonAltText = function() {
          return scope.onWatchlist ? 'Remove student ' + scope.sid + ' from my list' : 'Add student ' + scope.sid + ' to my list';
        };
        var buttonLabel = function() {
          return scope.onWatchlist ? 'remove from My List' : 'add to My List';
        };

        scope.buttonAltText = buttonAltText();
        scope.buttonLabel = buttonLabel();

        scope.toggle = function($event) {
          $event.stopPropagation();
          $event.preventDefault();
          // Choose proper factory method and then immediately toggle icon in UI
          var updateWatchlist = scope.onWatchlist ? watchlistFactory.removeFromWatchlist : watchlistFactory.addToWatchlist;
          scope.onWatchlist = !scope.onWatchlist;
          scope.buttonLabel = buttonLabel();
          scope.buttonAltText = buttonAltText();
          updateWatchlist(scope.sid).then(function() {
            return false;
          });
        };

        $rootScope.$on('watchlistAddition', function(event, sidAdded) {
          if (sidAdded === scope.sid) {
            scope.onWatchlist = true;
          }
        });

        $rootScope.$on('watchlistRemoval', function(event, sidRemoved) {
          if (sidRemoved === scope.sid) {
            scope.onWatchlist = false;
          }
        });
      }
    };
  });

}(window.angular));
