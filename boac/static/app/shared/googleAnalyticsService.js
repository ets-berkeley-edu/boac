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

  angular.module('boac').service('googleAnalyticsService', function($location, $rootScope, $timeout, config) {

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

    var trackPageView = function() {
      if (id) {
        ga('send', 'pageview', $location.path());

        if ($rootScope.me && $rootScope.me.isAuthenticated) {
          ga('set', 'uid', $rootScope.me.uid);
        }
      }
    };

    // Event fired when page is fully rendered
    $rootScope.$on('$viewContentLoaded', function() {
      $timeout(trackPageView, 0);
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
