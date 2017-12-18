(function(angular) {

  'use strict';

  angular.module('boac').service('boxplotService', function() {

    /**
     * Highcharts options shared between cohort-view and student-view boxplots.
     * @see http://api.highcharts.com/highcharts
     */
    var sharedBoxplotOptions = {
      chart: {
        backgroundColor: 'transparent',
        height: 18,
        inverted: true,
        // This unfortunate negative-margin hack compensates for an apparent Highcharts bug when rendering narrow boxplots.
        margin: [
          -5,
          0,
          0,
          0
        ],
        type: 'boxplot',
        width: 75
      },

      // Display no chart title, legend or watermark.
      credits: {
        enabled: false
      },

      legend: {
        enabled: false
      },

      title: {
        text: ''
      },

      // Display no axis labels.
      xAxis: {
        endOnTick: false,
        labels: {
          enabled: false
        },
        lineWidth: 0,
        startOnTick: false,
        tickLength: 0
      },

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

      plotOptions: {
        boxplot: {
          animation: false,
          color: '#ccc',
          fillColor: '#ccc',
          lineWidth: 1,
          medianColor: '#666',
          medianWidth: 3,
          whiskerLength: 9,
          whiskerWidth: 1
        }
      },

      series: {
        pointWidth: 9
      },

      tooltip: {
        shadow: false,
        // Render the tooltip as HTML so that it can overflow the boxplot container.
        useHTML: true
      }
    };

    var seriesOptionsForDataset = function(dataset) {
      return [
        {
          data: [
            [
              dataset.courseDeciles[0],
              dataset.courseDeciles[3],
              dataset.courseDeciles[5],
              dataset.courseDeciles[7],
              dataset.courseDeciles[10]
            ]
          ]
        },
        {
          data: [ [0, dataset.student.raw] ],
          marker: {
            fillColor: '#4a90e2',
            lineWidth: 0,
            radius: 4,
            states: {
              hover: {
                enabled: false
              }
            }
          },
          type: 'scatter'
        }
      ];
    };

    /**
     * Render a cohort-view boxplot from a given dataset to a given element.
     *
     * @param  {String}  elementId     Element id where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplotCohort = function(elementId, dataset) {
      // Options specific to a cohort-view boxplot and the provided dataset.
      var boxplotOptions = {
        chart: {
          renderTo: elementId
        },

        series: seriesOptionsForDataset(dataset),

        tooltip: {
          borderColor: 'transparent',
          headerFormat: '',
          hideDelay: 0,
          pointFormat: dataset.student.raw + ' Page Views (Class median is ' + dataset.courseDeciles[5] + ')',
          positioner: function(labelWidth, labelHeight) {
            return {
              x: -50,
              y: -1 * (labelHeight + 5)
            };
          },
          style: {
            color: '#fff'
          },
          width: 400
        }
      };

      _.merge(boxplotOptions, sharedBoxplotOptions);

      setTimeout(function() {
        return new Highcharts.Chart(boxplotOptions, 0);
      });
    };

    /**
     * Render a student-view boxplot from a given dataset to a given element.
     *
     * @param  {String}  elementId     Element id where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplotStudent = function(elementId, dataset) {
      // Options specific to a student-view boxplot and the provided dataset.
      var tooltipHeaderFormat = '<div class="student-profile-boxplot-container-tooltip-header">' +
                                '<div class="student-profile-boxplot-container-tooltip-label">User Score</div>' +
                                '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.student.raw + '</div>' +
                                '</div>';

      var tooltipBodyFormat = '<div class="student-profile-boxplot-container-tooltip-content">' +
                              '<div class="student-profile-boxplot-container-tooltip-row">' +
                              '<div class="student-profile-boxplot-container-tooltip-label">Maximum</div>' +
                              '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.courseDeciles[10] + '</div></div>' +
                              '<div class="student-profile-boxplot-container-tooltip-row">' +
                              '<div class="student-profile-boxplot-container-tooltip-label">70th Percentile</div>' +
                              '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.courseDeciles[7] + '</div></div>' +
                              '<div class="student-profile-boxplot-container-tooltip-row">' +
                              '<div class="student-profile-boxplot-container-tooltip-label">50th Percentile</div>' +
                              '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.courseDeciles[5] + '</div></div>' +
                              '<div class="student-profile-boxplot-container-tooltip-row">' +
                              '<div class="student-profile-boxplot-container-tooltip-label">30th Percentile</div>' +
                              '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.courseDeciles[3] + '</div></div>' +
                              '<div class="student-profile-boxplot-container-tooltip-row">' +
                              '<div class="student-profile-boxplot-container-tooltip-label">Minimum</div>' +
                              '<div class="student-profile-boxplot-container-tooltip-value">' + dataset.courseDeciles[0] + '</div></div>' +
                              '</div>';

      var boxplotOptions = {
        chart: {
          renderTo: elementId
        },

        series: seriesOptionsForDataset(dataset),

        tooltip: {
          borderColor: '#666',
          headerFormat: tooltipHeaderFormat,
          hideDelay: 0,
          pointFormat: tooltipBodyFormat,
          positioner: function() {
            return {
              x: 90,
              y: -75
            };
          },
          width: 400
        }
      };

      _.merge(boxplotOptions, sharedBoxplotOptions);

      setTimeout(function() {
        return new Highcharts.Chart(boxplotOptions, 0);
      });
    };

    return {
      drawBoxplotCohort: drawBoxplotCohort,
      drawBoxplotStudent: drawBoxplotStudent
    };
  });

}(window.angular));
