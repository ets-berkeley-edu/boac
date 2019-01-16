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

  angular.module('boac').factory('curatedCohortFactory', function($http, $rootScope, googleAnalyticsService) {

    var getStashedCohort = function(cohortId) {
      return _.find($rootScope.profile.myCuratedCohorts, ['id', cohortId]);
    };

    var addStudents = function(cohortId, sids) {
      var args = {
        curatedCohortId: cohortId,
        sids: sids
      };

      return $http.post('/api/curated_group/students/add', args).then(function(response) {
        var cohort = response.data;
        getStashedCohort(cohortId).studentCount = cohort.studentCount;
        googleAnalyticsService.track('Curated Cohort', 'add_students', cohort.name, cohort.id);
      });
    };

    var addStudent = function(cohortId, sid) {
      return $http.get('/api/curated_group/' + cohortId + '/add_student/' + sid).then(function(response) {
        var cohort = response.data;
        getStashedCohort(cohortId).studentCount = cohort.studentCount;
        googleAnalyticsService.track('Curated Cohort', 'add_student', cohort.name, cohort.id);
      });
    };

    var create = function(name, callback) {
      return $http.post('/api/curated_group/create', {name: name}).then(function(response) {
        var cohort = response.data;
        $rootScope.profile.myCuratedCohorts.push(cohort);
        googleAnalyticsService.track('Curated Cohort', 'create', cohort.name, cohort.id);
        var onCohortCreate = callback || _.noop;
        onCohortCreate(cohort);
      });
    };

    var deleteCuratedCohort = function(id) {
      return $http.delete('/api/curated_group/delete/' + id).then(function() {
        $rootScope.profile.myCuratedCohorts = _.remove($rootScope.profile.myCuratedCohorts, function(cohort) {
          return id !== cohort.id;
        });
        googleAnalyticsService.track('Curated Cohort', 'delete', null, id);
      });
    };

    var getStudentsWithAlertsInCohort = function(cohortId) {
      return $http.get('/api/curated_group/' + cohortId + '/students_with_alerts');
    };

    var getCuratedCohort = function(id) {
      return $http.get('/api/curated_group/' + id);
    };

    var getMyCuratedCohortIdsPerStudentId = function(sid) {
      return $http.get('/api/curated_groups/my/' + sid);
    };

    var removeStudent = function(cohortId, sid) {
      return $http.delete('/api/curated_group/' + cohortId + '/remove_student/' + sid).then(function(response) {
        var cohort = response.data;
        getStashedCohort(cohortId).studentCount = cohort.studentCount;
        googleAnalyticsService.track('Curated Cohort', 'remove_student', cohort.name, cohort.id);
      });
    };

    var rename = function(cohortId, name) {
      return $http.post('/api/curated_group/rename', {id: cohortId, name: name}).then(function(response) {
        var cohort = response.data;
        _.set(getStashedCohort(cohortId), 'name', cohort.name);
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
      getMyCuratedCohortIdsPerStudentId: getMyCuratedCohortIdsPerStudentId,
      getStudentsWithAlertsInCohort: getStudentsWithAlertsInCohort,
      removeStudent: removeStudent
    };
  });

}(window.angular));
