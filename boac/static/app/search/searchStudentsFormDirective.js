/**
 * Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.
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

  /**
   * Fall back to a default avatar in the case of an error during image load.
   */
  angular.module('boac').directive('searchStudentsForm', function(
    $location,
    $rootScope,
    $state,
    $transitions,
    page
  ) {

    $transitions.onStart({}, function($transition) {
      if (_.get($transition.$to(), 'name') !== 'search') {
        $rootScope.searchPhrase = null;
      }
    });

    $transitions.onFinish({}, function($transition) {
      $rootScope.transitionTo = _.get($transition.$to(), 'name');
    });

    return {
      restrict: 'E',
      scope: true,
      templateUrl: '/static/app/search/searchStudentsForm.html',

      link: function(scope, elem, attrs) {
        scope.searchPhrase = $location.search().q;
        scope.withButton = attrs.withButton;
        scope.includeCourses = attrs.includeCourses;
        scope.searchForStudents = function() {
          page.loading(true);
          $state.transitionTo('search', {q: scope.searchPhrase, includeCourses: scope.includeCourses}, {reload: true});
        };
      }
    };
  });

}(window.angular));
