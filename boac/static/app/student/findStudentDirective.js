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

  angular.module('boac').directive('findStudent', function() {

    return {
      // @see https://docs.angularjs.org/guide/directive#template-expanding-directive
      restrict: 'E',

      // @see https://docs.angularjs.org/guide/directive#isolating-the-scope-of-a-directive
      scope: {},
      templateUrl: '/static/app/student/findStudent.html',
      controller: function(studentFactory, $location, $q, $scope, $timeout) {

        $scope.$watch('selectedUID', function() {
          if (!_.isEmpty($scope.selectedUID)) {
            $location.path('/student/' + $scope.selectedUID);
            $location.replace();
          }
        });

        var loadOptions = function() {
          return studentFactory.getAllStudents('groupName').then(function(response) {
            var options = [];
            _.each(response.data, function(student) {
              _.each(student.athletics, function(a) {
                options.push({
                  uid: student.uid,
                  name: student.name + ' - ' + student.sid,
                  groupName: a.groupName
                });
              });
            });
            return options;
          });
        };

        var studentOptions = null;

        $scope.lazyLoadOptions = function() {
          if (!studentOptions) {
            var deferred = $q.defer();
            studentOptions = deferred.promise;

            $timeout(function() {
              loadOptions().then(deferred.resolve);
            }, 1000);
          }

          return studentOptions;
        };
      }
    };
  });

}(window.angular));
