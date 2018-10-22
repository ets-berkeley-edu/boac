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

  angular.module('boac').service('validationService', function($rootScope, authService) {

    var parseError = function(error) {
      $rootScope.pageTitle = 'Error';
      var message = error.message || _.get(error, 'data.message') || error || 'An unexpected server error occurred.';
      return {
        status: error.status || 500,
        message: _.truncate(message, {length: 200})
      };
    };

    var isReservedName = function(name) {
      return authService.isAscUser() && _.includes(['intensive students', 'inactive students'], name.toLowerCase());
    };

    /**
     * Verify that value of 'name' is non-empty, unique and not reserved.
     *
     * @param   {Cohort}      cohort                  Curated or filtered cohort
     * @param   {Function}    callback                Standard callback
     * @param   {String}      callback.errorMessage   Error description, if any
     * @returns {Object}                              Callback return object
     */
    var validateName = function(cohort, callback) {
      var errorMessage = null;
      if (_.isEmpty(cohort.name)) {
        errorMessage = 'Required';
      } else if (_.size(cohort.name) > 255) {
        errorMessage = 'Name must be 255 characters or fewer';
      } else if (isReservedName(cohort.name)) {
        errorMessage = 'Sorry, \'' + cohort.name + '\' is a reserved name. Please choose a different name.';
      } else {
        var allExisting = {
          'curated cohort': $rootScope.profile.myCuratedCohorts,
          'filtered cohort': $rootScope.profile.myFilteredCohorts
        };
        _.each(allExisting, function(cohorts, description) {
          _.each(cohorts, function(existingCohort) {
            var validate = !cohort.id || cohort.id !== existingCohort.id;
            if (validate && cohort.name === existingCohort.name) {
              errorMessage = 'You have an existing ' + description + ' with this name. Please choose a different name.';
              return false;
            }
          });
        });
      }
      return callback(errorMessage);
    };

    return {
      parseError: parseError,
      validateName: validateName
    };

  });
}(window.angular));
