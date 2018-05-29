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

  angular.module('boac').service('boxplotService', function(utilService) {

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
              dataset.currentScore.courseDeciles[0],
              dataset.currentScore.courseDeciles[3],
              dataset.currentScore.courseDeciles[5],
              dataset.currentScore.courseDeciles[7],
              dataset.currentScore.courseDeciles[10]
            ]
          ]
        },
        {
          data: [ [0, dataset.currentScore.student.raw] ],
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

    var describeLastActivity = function(dataset) {
      var daysSince = parseInt(_.get(dataset, 'lastActivity.student.daysSinceLastActivity'), 10);
      if (daysSince === null) {
        return 'Never visited course site.';
      }
      var inDays = 'Last visited course site ' + utilService.lastActivityDays(dataset).toLowerCase() + '.';
      var inContext = utilService.lastActivityInContext(dataset);
      return inContext ? inDays + ' ' + inContext : inDays;
    };

    /**
     * @param  {String}  element       Element where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplotCompact = function(element, dataset) {
      // Options specific to a cohort-view boxplot and the provided dataset.
      var boxplotOptions = {
        chart: {
          renderTo: element
        },

        series: seriesOptionsForDataset(dataset),

        tooltip: {
          borderColor: 'transparent',
          headerFormat: '',
          hideDelay: 0,
          pointFormat: describeLastActivity(dataset),
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
        try {
          var chart = new Highcharts.Chart(boxplotOptions, 0);
          // This tooltip-hiding event on the container element fires more reliably than the Highcharts default.
          element.addEventListener('mouseleave', function() {
            chart.tooltip.hide();
          });
          return chart;
        } catch (err) {
          /**
           * Highcharts error 13 (rendering div not found) may occur as a result of users navigating away from the
           * cohort list view, and should be handled silently. Unfortunately, we're stuck with a string match for
           * detecting it.
           * @see https://www.highcharts.com/errors/13
           */
          if (err.message.startsWith('Highcharts error #13')) {
            return;
          }
          throw err;
        }
      });
    };

    /**
     * @param  {String}  element       Element where the boxplot should be rendered
     * @param  {Object}  dataset       Dataset to render; 'courseDeciles' and 'student' properties are expected
     * @return {void}
     */
    var drawBoxplotStandard = function(element, dataset) {
      // Options specific to a student-view boxplot and the provided dataset.
      var tooltipHeaderFormat = '<div class="profile-tooltip-header">' +
                                '<div class="profile-tooltip-label">User Score</div>' +
                                '<div class="profile-tooltip-value">' + dataset.currentScore.student.raw + '</div>' +
                                '</div>';

      var tooltipBodyFormat = '<div class="profile-tooltip-content">' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-label">Maximum</div>' +
                              '<div class="profile-tooltip-value">' + dataset.currentScore.courseDeciles[10] + '</div></div>' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-label">70th Percentile</div>' +
                              '<div class="profile-tooltip-value">' + dataset.currentScore.courseDeciles[7] + '</div></div>' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-label">50th Percentile</div>' +
                              '<div class="profile-tooltip-value">' + dataset.currentScore.courseDeciles[5] + '</div></div>' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-label">30th Percentile</div>' +
                              '<div class="profile-tooltip-value">' + dataset.currentScore.courseDeciles[3] + '</div></div>' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-label">Minimum</div>' +
                              '<div class="profile-tooltip-value">' + dataset.currentScore.courseDeciles[0] + '</div></div>' +
                              '</div>';

      var boxplotOptions = {
        chart: {
          renderTo: element
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

    var drawBoxplot = function(element, dataset, compactTooltip) {
      if (compactTooltip) {
        drawBoxplotCompact(element, dataset);
      } else {
        drawBoxplotStandard(element, dataset);
      }
    };

    return {
      drawBoxplot: drawBoxplot
    };
  });

}(window.angular));
