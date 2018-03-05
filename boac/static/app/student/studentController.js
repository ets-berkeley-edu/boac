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

  angular.module('boac').controller('StudentController', function(
    authService,
    boxplotService,
    config,
    courseFactory,
    googleAnalyticsService,
    studentFactory,
    watchlistFactory,
    $base64,
    $location,
    $scope,
    $stateParams
  ) {

    $scope.demoMode = config.demoMode;

    $scope.student = {
      canvasProfile: null,
      enrollmentTerms: null,
      isLoading: true
    };

    $scope.showAllTerms = false;
    $scope.showDismissedAlerts = false;

    $scope.dismissAlert = function(alertId) {
      studentFactory.dismissAlert(alertId).then(function() {
        var dismissed = _.remove($scope.alerts.shown, {id: alertId});
        Array.prototype.push.apply($scope.alerts.dismissed, dismissed);
      }).catch(function(error) {
        if (error.data) {
          $scope.error = _.truncate(error.data.message, {length: 200}) || 'An unexpected server error occurred.';
        } else {
          throw error;
        }
      });
    };

    $scope.goToCourse = function(event, termId, sectionId) {
      event.stopPropagation();
      $location.path('/course/' + termId + '/' + sectionId);
    };

    var showUnitsChart = function() {
      var cumulativeUnits = _.get($scope.student, 'sisProfile.cumulativeUnits');
      var currentEnrolledUnits = _.get($scope.student, 'enrollmentTerms[0].enrolledUnits');
      var tooltipBodyFormat = '<div class="profile-tooltip-content">' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-swatch" style="background-color:#aec9eb"></div>' +
                              '<div class="profile-tooltip-label">Cumulative Units</div>' +
                              '<div class="profile-tooltip-value">' + cumulativeUnits + '</div></div>' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-swatch" style="background-color:#d6e4f9"></div>' +
                              '<div class="profile-tooltip-label">Currently Enrolled Units</div>' +
                              '<div class="profile-tooltip-value">' + currentEnrolledUnits + '</div></div>' +
                              '</div>';
      var unitsChartOptions = {
        chart: {
          backgroundColor: 'transparent',
          height: 60,
          inverted: true,
          spacingLeft: 5,
          type: 'column',
          width: 170
        },
        credits: {
          enabled: false
        },
        legend: {
          enabled: false
        },
        navigation: {
          buttonOptions: {
            enabled: false
          }
        },
        title: {
          text: ''
        },
        tooltip: {
          borderColor: '#666',
          headerFormat: '',
          hideDelay: 0,
          pointFormat: tooltipBodyFormat,
          positioner: function() {
            return {
              x: -35,
              y: 35
            };
          },
          width: 240,
          shadow: false,
          useHTML: true
        },
        xAxis: {
          labels: {
            enabled: false
          },
          lineWidth: 0,
          startOnTick: false,
          tickLength: 0
        },
        yAxis: {
          min: 0,
          max: 120,
          gridLineColor: '#000000',
          tickInterval: 30,
          labels: {
            align: 'center',
            distance: 0,
            overflow: false,
            style: {
              color: '#999999',
              fontFamily: 'Helvetica, Arial, sans',
              fontSize: '12px',
              fontWeight: 'bold'
            }
          },
          stackLabels: {
            enabled: false
          },
          title: {
            enabled: false
          },
          gridZIndex: 1000
        },
        plotOptions: {
          column: {
            stacking: 'normal',
            groupPadding: 0,
            pointPadding: 0
          },
          series: {
            states: {
              hover: {
                enabled: false
              }
            }
          }
        },
        colors: ['#d6e4f9', '#aec9eb'],
        series: [
          {
            name: 'Term units',
            data: [ currentEnrolledUnits ]
          },
          {
            name: 'Cumulative units',
            data: [ cumulativeUnits ]
          }
        ]
      };
      setTimeout(function() {
        Highcharts.chart('profile-units-chart-container', unitsChartOptions);
      });
    };

    var loadStudent = function(uid) {
      $scope.student.isLoading = true;
      studentFactory.analyticsPerUser(uid).then(function(analytics) {
        $scope.student = analytics.data;
        // Track view event
        var preferredName = $scope.student.sisProfile && $scope.student.sisProfile.preferredName;
        _.each($scope.student.enrollmentTerms, function(term) {
          // Merge in unmatched canvas sites
          var unmatched = _.map(term.unmatchedCanvasSites, function(c) {
            // course_code is often valuable (eg, 'ECON 1 - LEC 001'), occasionally not (eg, CCN). Use it per strict criteria:
            var useCourseCode = (/^[A-Z].*[A-Za-z]{3} \d/).test(c.courseCode);
            return _.merge(c, {
              displayName: useCourseCode ? c.courseCode : c.courseName,
              title: useCourseCode ? c.courseName : null,
              canvasSites: [ c ]
            });
          });
          term.enrollments = _.concat(term.enrollments, unmatched);
          _.each(term.enrollments, function(course) {
            _.each(course.sections, function(section) {
              course.waitlisted = section.enrollmentStatus === 'W';
              // Break if waitlisted
              return !course.waitlisted;
            });
          });
        });
        googleAnalyticsService.track('student', 'view-profile', preferredName, parseInt(uid, 10));
      }).catch(function(error) {
        var message = error.message || _.get(error, 'data.message') || 'An unexpected server error occurred.';
        $scope.error = _.truncate(message, {length: 200});
      }).then(function() {
        var athleticsProfile = $scope.student.athleticsProfile;
        if (athleticsProfile) {
          athleticsProfile.fullName = athleticsProfile.firstName + ' ' + athleticsProfile.lastName;
          if (athleticsProfile.sid) {
            studentFactory.getAlerts(athleticsProfile.sid).then(function(alerts) {
              $scope.alerts = alerts.data;
            });
            showUnitsChart();
          }
        }
      }).then(function() {
        courseFactory.getSectionIdsPerTerm().then(function(response) {
          $scope.sectionIdsPerTerm = response.data;
          $scope.student.isLoading = false;
        });
      });
    };

    var prepareReturnUrl = function(uid) {
      var encodedReturnUrl = $location.search().r;
      if (!_.isEmpty(encodedReturnUrl)) {
        // Parse referring URL, remove CAS login param if present, and add anchor param with current UID.
        $location.search('r', null).replace();
        var url = $base64.decode(decodeURIComponent(encodedReturnUrl));
        var anchorParam = 'a=' + uid;
        var urlComponents = url.split('?');
        if (urlComponents.length > 1) {
          url = urlComponents.shift();
          var query = urlComponents.join('?');
          query = query.replace(/&?casLogin=true/, '');
          if (query.length) {
            anchorParam = query + '&' + anchorParam;
          }
        }
        $scope.returnUrl = url + '?' + anchorParam;
        $scope.hideFeedbackLink = true;
      }
    };

    var init = function() {
      var uid = $stateParams.uid;
      loadStudent(uid);
      prepareReturnUrl(uid);
      $scope.isWatchlistLoading = true;
      watchlistFactory.getMyWatchlist().then(function(response) {
        $scope.myWatchlist = response.data;
        $scope.isWatchlistLoading = false;
      });
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
      boxplotService.drawBoxplotStudent(elementId, course.analytics[metric]);
    };

    init();
  });

}(window.angular));
