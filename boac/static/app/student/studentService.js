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

  angular.module('boac').service('studentService', function() {

    var showUnitsChart = function(student) {
      var cumulativeUnits = _.get(student, 'sisProfile.cumulativeUnits');
      var currentEnrolledUnits = _.get(student, 'enrollmentTerms[0].enrolledUnits');
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

    return {
      showUnitsChart: showUnitsChart
    };
  });

}(window.angular));
