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

  angular.module('boac').service('googleAnalyticsService', function($rootScope, $transitions, config) {

    // Disable Google Analytics with id=False in py config file
    var id = config.googleAnalyticsId;

    /**
     * See https://developers.google.com/analytics/devguides/collection/analyticsjs/events
     *
     * @param  {String}    category  For example, 'cohort'
     * @param  {String}    action    For example, 'delete'
     * @param  {String}    label     For example, cohort name
     * @param  {String}    value     For example, cohort id
     * @return {void}
     */
    var track = function(category, action, label, value) {
      if (id) {
        ga('send', 'event', category, action, label, value, {
          userId: _.get($rootScope.me, 'uid')
        });
      }
    };

    $transitions.onSuccess({}, function() {
      if (id) {
        var uid = _.get($rootScope.me, 'uid');
        ga('create', id, 'auto');
        if (uid) {
          ga('set', 'userId', uid);
        }
        ga('send', 'pageview');
      }
    });

    return {
      track: track
    };
  });

}(window.angular));
