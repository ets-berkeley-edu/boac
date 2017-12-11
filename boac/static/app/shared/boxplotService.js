(function(angular) {

  'use strict';

  angular.module('boac').service('boxplotService', function() {

    /**
     * Highcharts options shared between minified and non-minified boxplots.
     * @see http://api.highcharts.com/highcharts
     */
    var sharedBoxplotOptions = {
      chart: {
        backgroundColor: 'transparent',
        inverted: true,
        type: 'boxplot'
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
          color: '#ccc',
          fillColor: '#ccc',
          lineWidth: 1,
          medianColor: '#666',
          medianWidth: 3
        }
      },

      tooltip: {
        shadow: false,
        style: {
          color: '#fff'
        },
        // Render the tooltip as HTML so that it can overflow the boxplot container.
        useHTML: true
      }
    };

    /**
     * Render a non-minified boxplot from a given dataset to a given element.
     *
     * @param  {String}  elementId     Element id where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplot = function(elementId, dataset) {
      // Options specific to a non-minified boxplot and the provided dataset.
      var boxplotOptions = {
        chart: {
          margin: [
            0,
            20,
            0,
            20
          ],
          renderTo: elementId
        },

        plotOptions: {
          boxplot: {
            whiskerLength: 20,
            whiskerWidth: 3
          }
        },

        series: [
          {
            data: [
              [
                dataset.courseDeciles[0],
                dataset.courseDeciles[3],
                dataset.courseDeciles[5],
                dataset.courseDeciles[7],
                dataset.courseDeciles[10]
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
          },
          {
            data: [ [0, dataset.student.raw] ],
            marker: {
              fillColor: '#4a90e2',
              lineWidth: 5,
              lineWidthPlus: 2,
              lineColor: '#4a90e2',
              radius: 5,
              radiusPlus: 2
            },
            tooltip: {
              headerFormat: '',
              pointFormat: 'User score: {point.y}'
            },
            type: 'scatter'
          }
        ],

        tooltip: {
          hideDelay: 100,
          positioner: function(labelWidth, labelHeight) {
            return {
              x: 305,
              y: 15 - labelHeight / 2
            };
          }
        }
      };

      _.merge(boxplotOptions, sharedBoxplotOptions);

      setTimeout(function() {
        return new Highcharts.Chart(boxplotOptions, 0);
      });
    };

    /**
     * Render a minified boxplot from a given dataset to a given element.
     *
     * @param  {String}  elementId     Element id where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplotMinified = function(elementId, dataset) {
      // Options specific to a minified boxplot and the provided dataset.
      var boxplotOptions = {
        chart: {
          // This unfortunate negative-margin hack compensates for an apparent Highcharts bug when rendering narrow boxplots.
          margin: [
            -5,
            0,
            0,
            0
          ],
          renderTo: elementId
        },

        plotOptions: {
          boxplot: {
            animation: false,
            whiskerLength: 9,
            whiskerWidth: 1
          }
        },

        series: [
          {
            data: [
              [
                dataset.courseDeciles[0],
                dataset.courseDeciles[3],
                dataset.courseDeciles[5],
                dataset.courseDeciles[7],
                dataset.courseDeciles[10]
              ]
            ],
            pointWidth: 9
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
        ],

        tooltip: {
          headerFormat: '',
          hideDelay: 0,
          pointFormat: dataset.student.raw + ' Page Views (Class median is ' + dataset.courseDeciles[5] + ')',
          positioner: function(labelWidth, labelHeight) {
            return {
              x: -50,
              y: -1 * (labelHeight + 5)
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
      drawBoxplot: drawBoxplot,
      drawBoxplotMinified: drawBoxplotMinified
    };
  });

}(window.angular));
