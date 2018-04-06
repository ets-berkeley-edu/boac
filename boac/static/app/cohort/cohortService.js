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

  angular.module('boac').service('cohortService', function(cohortFactory, config, utilService) {

    var validateCohortLabel = function(cohort, callback) {
      if (_.includes(['Intensive', 'Inactive'], cohort.label)) {
        return callback('Sorry, \'' + cohort.label + '\' is a reserved name. Please choose a different name.');
      }
      var error = null;
      cohortFactory.getMyCohorts().then(function(response) {
        _.each(response.data, function(next) {
          var validate = !cohort.id || cohort.id !== next.id;
          if (validate && cohort.label === next.label) {
            error = 'You have a cohort with this name. Please choose a different name.';
            return false;
          }
        });
      }).then(function() {
        return callback(error);
      });
    };

    var decorateCohortAlerts = function(cohort) {
      if (cohort.alerts && cohort.alerts.length) {
        cohort.alerts = {
          isCohortAlerts: true,
          students: utilService.extendSortableNames(cohort.alerts),
          sortBy: 'sortableName',
          reverse: false
        };
      }
    };

    var loadMyCohorts = function(callback) {
      cohortFactory.getMyCohorts().then(function(cohortsResponse) {
        var myCohorts = [];
        _.each(cohortsResponse.data, function(cohort) {
          decorateCohortAlerts(cohort);
          myCohorts.push(cohort);
        });
        return callback(myCohorts);
      });
    };

    return {
      decorateCohortAlerts: decorateCohortAlerts,
      loadMyCohorts: loadMyCohorts,
      validateCohortLabel: validateCohortLabel
    };

  });
}(window.angular));
