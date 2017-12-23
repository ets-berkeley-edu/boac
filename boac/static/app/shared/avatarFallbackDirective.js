(function(angular) {

  'use strict';

  /**
   * Fall back to a default avatar in the case of an error during image load.
   */
  angular.module('boac').directive('avatarFallback', function() {
    var fallbackPath = '/static/app/shared/avatar-50.png';
    return {
      link: function(scope, elm, attrs) {
        elm.bind('error', function() {
          if (attrs.src !== fallbackPath) {
            attrs.$set('src', fallbackPath);
          }
        });
      }
    };
  });

}(window.angular));
