(function(angular) {

  'use strict';

  angular.module('boac').service('googleAnalyticsService', function(config, $rootScope, $location) {

    // Disable Google Analytics with id=False in py config file
    var id = config.googleAnalyticsId;

    /**
     * @param  {String}    category     Eg, 'cohort'
     * @param  {String}    action       Eg, 'create'
     * @param  {String}    [label]      [Optional] Eg, 'Golfers with a low GPA'
     * @param  {Number}    [value]      [Optional] Eg, 23 (id of new cohort)
     * @return {void}
     */
    var track = function(category, action, label, value) {
      if (id) {
        var fields = {
          hitType: 'event',
          eventCategory: category,
          eventAction: action
        };
        if (label) {
          fields.eventLabel = label;
        }
        if (value) {
          fields.eventValue = parseInt(value, 10);
        }
        ga('send', fields);
      }
    };

    // Event fired when page is fully rendered
    $rootScope.$on('$viewContentLoaded', function() {
      if (id) {
        ga('send', 'pageview', $location.path());

        var user = $rootScope.me.authenticated_as;
        if (user.is_authenticated) {
          ga('set', 'uid', user.uid);
        }
      }
    });

    /**
     * Register googleAnalyticsId per https://developers.google.com/analytics
     *
     * @return {void}
     */
    var googleAnalytics = function() {
      if (id) {
        /* eslint-disable */
        window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;
        /* eslint-enable */
        ga('create', id, 'auto');
      }
    };

    googleAnalytics();

    return {
      track: track
    };
  });

}(window.angular));
