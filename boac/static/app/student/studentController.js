(function(angular) {

  'use strict';

  angular.module('boac').controller('StudentController', function(
    authService,
    boxplotService,
    googleAnalyticsService,
    studentFactory,
    $scope,
    $stateParams
  ) {

    var loadAnalytics = authService.authWrap(function() {
      var uid = $stateParams.uid;

      $scope.student.isLoading = true;
      studentFactory.analyticsPerUser(uid).then(function(analytics) {
        $scope.student = analytics.data;
        // Track view event
        var preferredName = $scope.student.sisProfile && $scope.student.sisProfile.preferredName;
        googleAnalyticsService.track('student', 'view-profile', preferredName, parseInt(uid, 10));
      }).catch(function(error) {
        $scope.error = _.truncate(error.data.message, {length: 200}) || 'An unexpected server error occurred.';
      }).then(function() {
        $scope.student.isLoading = false;
      });
    });

    $scope.student = {
      canvasProfile: null,
      enrollmentTerms: null,
      isLoading: true
    };

    $scope.drawBoxplot = function(termId, displayName, courseId, metric) {
      var term = _.find($scope.student.enrollmentTerms, {termId: termId});

      var courseSites;
      if (displayName === 'unmatchedCanvasSites') {
        courseSites = term.unmatchedCanvasSites;
      } else {
        var enrollment = _.find(term.enrollments, {displayName: displayName});
        courseSites = enrollment.canvasSites;
      }

      var course = _.find(courseSites, {canvasCourseId: courseId});
      var elementId = 'boxplot-' + courseId + '-' + metric;
      boxplotService.drawBoxplot(elementId, course.analytics[metric]);
    };

    loadAnalytics();
  });

}(window.angular));
