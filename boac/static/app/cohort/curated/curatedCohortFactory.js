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

  var boac = angular.module('boac');

  boac.factory('curatedCohortFactory', function($http, $rootScope, googleAnalyticsService) {

    var addStudents = function(cohort, students) {
      var args = {
        curatedCohortId: cohort.id,
        sids: _.map(students, 'sid')
      };
      return $http.post('/api/curated_cohort/students/add', args).then(function() {
        _.each(students, function(student) {
          $rootScope.$broadcast('addStudentToCuratedCohort', {cohort: cohort, student: student});
        });
        googleAnalyticsService.track('Curated Cohort', 'add_students', cohort.name, cohort.id);
      });
    };

    var addStudent = function(cohort, student) {
      return $http.get('/api/curated_cohort/' + cohort.id + '/add_student/' + student.sid).then(function() {
        $rootScope.$broadcast('addStudentToCuratedCohort', {cohort: cohort, student: student});
      });
    };

    var create = function(name) {
      return $http.post('/api/curated_cohort/create', {name: name}).then(function(response) {
        var cohort = response.data;
        $rootScope.$broadcast('curatedCohortCreated', {cohort: cohort});
        googleAnalyticsService.track('Curated Cohort', 'create', cohort.name, cohort.id);
      });
    };

    var deleteCuratedCohort = function(id) {
      return $http.delete('/api/curated_cohort/delete/' + id).then(function() {
        $rootScope.$broadcast('curatedCohortDeleted', {cohortId: id});
        googleAnalyticsService.track('Curated Cohort', 'delete', null, id);
      });
    };

    var getStudentsWithAlertsInCohort = function(cohortId) {
      return $http.get('/api/curated_cohort/' + cohortId + '/students_with_alerts');
    };

    var getCuratedCohort = function(id) {
      return $http.get('/api/curated_cohort/' + id);
    };

    var removeStudent = function(cohort, student) {
      return $http.delete('/api/curated_cohort/' + cohort.id + '/remove_student/' + student.sid).then(function() {
        $rootScope.$broadcast('removeStudentFromCuratedCohort', {cohort: cohort, student: student});
      });
    };

    var rename = function(cohortId, name) {
      return $http.post('/api/curated_cohort/rename', {id: cohortId, name: name}).then(function(response) {
        var cohort = response.data;
        $rootScope.$broadcast('curatedCohortRenamed', {cohort: cohort});
        googleAnalyticsService.track('Curated Cohort', 'rename', cohort.name, cohort.id);
      });
    };

    return {
      addStudents: addStudents,
      addStudent: addStudent,
      rename: rename,
      create: create,
      deleteCuratedCohort: deleteCuratedCohort,
      getCuratedCohort: getCuratedCohort,
      getStudentsWithAlertsInCohort: getStudentsWithAlertsInCohort,
      removeStudent: removeStudent
    };
  });

}(window.angular));
