/**
 * Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.
 *
 * Permission to use, copy, modify, and distribute this software and its documentation
 * for educational, research, and not-for-profit purposes, without fee and without a
 * signed licensing agreement, is hereby granted, provided that the above copyright
 * notice, this paragraph and the following two paragraphs appear in all copies,
 * modifications, and distributions.
 *
 * Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
 * Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
 * http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
 *
 * IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 * INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 * THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
 * SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
 * "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 */

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
