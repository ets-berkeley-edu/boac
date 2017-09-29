(function(angular) {

  'use strict';

  angular.module('boac').controller('StudentController', function(analyticsFactory, authService, $rootScope, $scope, $stateParams) {

    var loadAnalytics = function() {
      if (authService.isAuthenticatedUser()) {
        $scope.student.isLoading = true;
        analyticsFactory.analyticsPerUser($stateParams.uid).then(function(analytics) {
          $scope.student = analytics.data;
        }).catch(function(error) {
          $scope.error = _.truncate(error.message, {length: 200});
        }).then(function() {
          $scope.student.isLoading = false;
        });
      }
    };

    $scope.student = {
      canvasProfile: null,
      courses: null,
      isLoading: true
    };

    /**
     * Render a box plot for a given course and metric
     *
     * @param  {Number}  courseId      Canvas course ID for the course
     * @param  {String}  metric        Metric to draw the boxplot for
     * @return {void}
     */
    $scope.drawBoxplot = function(courseId, metric) {

      var course = _.find($scope.student.courses, {canvasCourseId: courseId});

      setTimeout(function() {
        // Render the box plot using highcharts
        // @see http://api.highcharts.com/highcharts
        return new Highcharts.Chart({
          chart: {
            backgroundColor: 'transparent',
            inverted: true,
            // Ensure that the box plot is displayed horizontally
            margin: [
              0,
              20,
              0,
              20
            ],
            renderTo: 'boxplot-' + courseId + '-' + metric,
            type: 'boxplot'
          },

          title: {
            // Ensure that no chart title is rendered
            text: ''
          },

          legend: {
            // Ensure that no legend is rendered
            enabled: false
          },

          credits: {
            // Ensure that no highcarts watermark is rendered
            enabled: false
          },

          tooltip: {
            hideDelay: 100,
            positioner: function(labelWidth, labelHeight) {
              // Ensure that the tooltip does not overlap with the box plot to
              // allow access hover access to 'my points'
              return {
                x: 305,
                y: 15 - labelHeight / 2
              };
            },
            shadow: false,
            style: {
              color: '#FFF'
            },
            // Ensure the tooltip is rendered as HTML to allow it
            // to overflow the box plot container
            useHTML: true
          },

          // Ensure that no x-axis labels or lines are shown and
          // that the box plot takes up the maximum amount of space
          xAxis: {
            endOnTick: false,
            labels: {
              enabled: false
            },
            lineWidth: 0,
            startOnTick: false,
            tickLength: 0
          },

          // Ensure that no y-axis labels or lines are shown and
          // that the box plot takes up the maximum amount of space
          yAxis: {
            endOnTick: false,
            gridLineWidth: 0,
            labels: {
              enabled: false
            },
            lineWidth: 0,
            maxPadding: 0.001,
            minPadding: 0.001,
            startOnTick: false,
            tickLength: 0,
            title: {
              enabled: false
            }
          },

          // Style the box plot
          plotOptions: {
            boxplot: {
              color: '#88ACC4',
              fillColor: '#88ACC4',
              lineWidth: 1,
              medianColor: '#EEE',
              medianWidth: 3,
              whiskerLength: 20,
              whiskerWidth: 3
            }
          },

          series: [
            // Box plot data series
            {
              data: [
                [
                  course.analytics[metric].courseDeciles[0],
                  course.analytics[metric].courseDeciles[3],
                  course.analytics[metric].courseDeciles[5],
                  course.analytics[metric].courseDeciles[7],
                  course.analytics[metric].courseDeciles[10]
                ]
              ],
              pointWidth: 40,
              tooltip: {
                headerFormat: '',
                pointFormat: 'Maximum: {point.high}<br/>' +
                             '70th percentile: {point.q3}<br/>' +
                             '50th percentile: {point.median}<br/>' +
                             '30th percentile: {point.q1}<br/>' +
                             'Minimum: {point.low}',
                borderColor: 'transparent'
              }
              // Current user points
            },
            {
              data: [ [0, course.analytics[metric].student.raw] ],
              marker: {
                fillColor: '#3179BC',
                lineWidth: 5,
                lineColor: '#3179BC'
              },
              tooltip: {
                headerFormat: '',
                pointFormat: 'User score: {point.y}'
              },
              type: 'scatter'
            }
          ]
        });
      }, 0);
    };

    $scope.percentile = function(courseData) {
      var rawPercentile = courseData.student.percentile;
      if (!rawPercentile && rawPercentile !== 0) {
        return 'No data';
      }
      var percentileRounded = _.round(rawPercentile);

      /* eslint-disable no-fallthrough */
      switch (percentileRounded % 10) {
        case 1:
          if (percentileRounded !== 11) { return percentileRounded + 'st percentile'; }
        case 2:
          if (percentileRounded !== 12) { return percentileRounded + 'nd percentile'; }
        case 3:
          if (percentileRounded !== 13) { return percentileRounded + 'rd percentile'; }
        default:
          return percentileRounded + 'th percentile';
      }
    };

    $rootScope.$on('userStatusChange', loadAnalytics);

    loadAnalytics();
  });

}(window.angular));
