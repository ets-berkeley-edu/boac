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

  angular.module('boac').controller('SearchController', function(
    $location,
    $scope,
    authService,
    config,
    page,
    studentFactory,
    utilService,
    validationService
  ) {

    $scope.demoMode = config.demoMode;
    $scope.search = {
      limit: 50,
      phrase: $location.search().q,
      students: null,
      totalStudentCount: null
    };

    var courseSortOptions = $scope.courseSortOptions = {
      reverse: false,
      sortBy: 'section'
    };

    $scope.courseSort = function(sortBy) {
      if (courseSortOptions.sortBy === sortBy) {
        courseSortOptions.reverse = !courseSortOptions.reverse;
      } else {
        courseSortOptions.sortBy = sortBy;
        courseSortOptions.reverse = false;
      }
      $scope.coursesResorted = true;
    };

    var splitCourseName = function(name) {
      var split = name.split(' ');
      return [split.slice(0, -1).join(' '), split[split.length - 1]];
    };

    $scope.courseComparator = function(course1, course2) {
      // If sorting by title, return string comparison.
      if ((courseSortOptions.sortBy === 'title') && (course1.value.courseTitle !== course2.value.courseTitle)) {
        return (course1.value.courseTitle > course2.value.courseTitle) ? 1 : -1;
      }
      // If sorting by section name, attempt to compare by subject area.
      var splitName1 = splitCourseName(course1.value.courseName);
      var splitName2 = splitCourseName(course2.value.courseName);
      if (splitName1[0] > splitName2[0]) {
        return 1;
      }
      if (splitName1[0] < splitName2[0]) {
        return -1;
      }
      // If subject areas are identical, extract and compare numeric portion of catalog id.
      var numericCode1 = parseInt(splitName1[1].match(/\d+/)[0], 10);
      var numericCode2 = parseInt(splitName2[1].match(/\d+/)[0], 10);
      if (numericCode1 > numericCode2) {
        return 1;
      }
      if (numericCode1 < numericCode2) {
        return -1;
      }
      // If catalog ids are numerically indentical, handle prefixes and suffixes with alphabetic comparison.
      if (splitName1[1] > splitName2[1]) {
        return 1;
      }
      if (splitName1[1] < splitName2[1]) {
        return -1;
      }
      // Instruction format and section number.
      if (course1.value.instructionFormat > course2.value.instructionFormat) {
        return 1;
      }
      if (course1.value.instructionFormat < course2.value.instructionFormat) {
        return -1;
      }
      return (course1.value.sectionNum > course2.value.sectionNum) ? 1 : -1;
    };

    var loadSearchResults = function() {
      var inactiveAsc = authService.isAscUser() ? false : null;
      page.loading(true);
      studentFactory.searchForStudents($scope.search.phrase, inactiveAsc, 'last_name', 0, $scope.search.limit).then(
        function(response) {
          $scope.search.courses = response.data.courses;
          $scope.search.students = utilService.extendSortableNames(response.data.students);
          _.each($scope.search.students, function(student) {
            student.alertCount = student.alertCount || 0;
            student.term = student.term || {};
            student.term.enrolledUnits = student.term.enrolledUnits || 0;
          });
          $scope.search.totalCourseCount = response.data.totalCourseCount;
          $scope.search.totalStudentCount = response.data.totalStudentCount;
        },
        function(err) {
          $scope.error = validationService.parseError(err);
        }
      ).then(function() {
        page.loading(false);
      });
    };

    $scope.$watch('displayOptions.sortBy', function(value) {
      if (!_.isNil(value) && !page.isLoading()) {
        $location.search('s', $scope.displayOptions.sortBy);
      }
    });

    $scope.$watch('displayOptions.reverse', function(value) {
      if (!_.isNil(value) && !page.isLoading()) {
        $location.search('r', value.toString());
      }
    });

    var init = function() {
      if ($scope.search.phrase) {
        var args = _.clone($location.search());
        $scope.displayOptions = {
          curatedCohort: true,
          reverse: utilService.toBoolOrNull(args.r),
          sortBy: _.includes(['sid', 'sortableName'], args.s) ? args.s : 'sortableName'
        };
        loadSearchResults();
      } else {
        $scope.error = {message: 'No search input found.'};
      }
    };

    init();
  });

}(window.angular));
