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

  angular.module('boac').service('visualizationService', function($location, config) {

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

    var drawScatterplot = function(students, yAxisMeasure, goToUserPage) {
      var svg;

      function x(d) { return d.analytics.lastActivity.percentile; }
      function y(d) { return _.get(d, yAxisMeasure).percentile; }
      function key(d) { return d.uid; }

      var yAxisName = 'Assignments Submitted';
      if (yAxisMeasure === 'analytics.currentScore') {
        yAxisName = 'Assignment grades';
      }

      var width = 910;
      var height = 500;

      var xScale = d3.scaleLinear().domain([0, 100]).range([0, width]).nice();
      var yScale = d3.scaleLinear().domain([0, 100]).range([height, 0]).nice();

      var xAxis = d3.axisBottom(xScale)
        .ticks(10, d3.format(',d'))
        .tickSize(-height);

      var yAxis = d3.axisLeft(yScale)
        .ticks(10, d3.format(',d'))
        .tickSize(-width);

      var container = d3.select('#matrix-container');

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3.select('#scatterplot')
        .html('')
        .append('svg')
        .attr('class', 'matrix-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('stroke', 1);

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'matrix-gradient-rect')
        .attr('fill', 'url(#matrix-background-gradient)');

      svg.append('g')
        .attr('class', 'x matrix-axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

      // Add the y-axis.
      svg.append('g')
        .attr('class', 'y matrix-axis')
        .call(yAxis);

      var defs = svg.append('svg:defs');

      var linearGradient = defs.append('linearGradient')
        .attr('id', 'matrix-background-gradient')
        .attr('x1', '0%')
        .attr('y1', '100%')
        .attr('x2', '100%')
        .attr('y2', '0%')
        .attr('spreadMethod', 'pad');
      linearGradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', '#ffe5e5')
        .attr('stop-opacity', '1');
      linearGradient.append('stop')
        .attr('offset', '50%')
        .attr('stop-color', '#fffde5')
        .attr('stop-opacity', '1');
      linearGradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', '#e8ffe5')
        .attr('stop-opacity', '1');

      defs.append('svg:clipPath')
        .attr('id', 'clip-inner')
        .append('svg:rect')
        .attr('id', 'clip-rect-inner')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', width)
        .attr('height', height);

      var avatarBackgroundPath = '/static/app/shared/avatar-50.png';

      function avatar(d) {
        var avatarId = 'avatar_' + d.uid;
        var pattern = defs.append('svg:pattern')
          .attr('id', avatarId)
          .attr('width', '100%')
          .attr('height', '100%')
          .attr('patternContentUnits', 'objectBoundingBox');
        var photoUri = config.demoMode.blur ? avatarBackgroundPath : '/api/student/' + d.uid + '/photo';
        var avatarImage = pattern.append('svg:image')
          .attr('xlink:href', photoUri)
          .attr('width', 1)
          .attr('height', 1)
          .attr('preserveAspectRatio', 'xMidYMid slice');
        avatarImage.on('error', function() {
          avatarImage.attr('xlink:href', avatarBackgroundPath);
        });
        return 'url(#' + avatarId + ')';
      }

      var objects = svg.append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .classed('matrix-svg', true)
        .classed('objects', true);

      objects.append('svg:defs')
        .append('svg:clipPath')
        .attr('id', 'clip')
        .append('svg:rect')
        .attr('id', 'clip-rect')
        .attr('x', -55)
        .attr('y', -55)
        .attr('width', width + 110)
        .attr('height', height + 110);

      var dotGroup = objects.append('g')
        .attr('clip-path', 'url(#clip)');

      var dot = dotGroup.attr('class', 'dots')
        .selectAll('.dot')
        .data(students, key)
        .enter().append('circle')
        .attr('class', 'dot')
        .style('fill', '#8bbdda')
        .style('opacity', 0.66)
        .style('stroke-width', 0)
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', 9);

      // Add x-axis labels.
      svg.append('text')
        .attr('class', 'matrix-axis-title')
        .attr('x', width / 2)
        .attr('y', height + 25)
        .text('Days since bCourses course site viewed');
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', 0)
        .attr('y', height + 22)
        .text('Previously');
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', width)
        .attr('y', height + 22)
        .text('Recently');

      // Add y-axis labels.
      svg.append('text')
        .attr('class', 'matrix-axis-title')
        .attr('y', -20)
        .attr('x', 0 - (height / 2))
        .attr('transform', 'rotate(-90)')
        .text(yAxisName);
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', -10)
        .attr('y', height - 2)
        .text('Low');
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', -10)
        .attr('y', 10)
        .text('High');

      var displayValue = function(d, prop) {
        var value = _.get(d, prop + '.displayPercentile');
        if (!value) {
          return 'No data';
        }
        return value + ' percentile';
      };

      dot.on('click', function(d) {
        goToUserPage(d.uid);
      });

      var onDotSelected = function(d) {
        // Clear any existing tooltips.
        container.selectAll('.matrix-tooltip').remove();

        // Move dot to front.
        this.parentNode.appendChild(this);
        // Stroke highlight.
        var selection = d3.select(this);
        selection.attr('r', '45')
          .style('stroke-width', 5)
          .style('stroke', '#ccc')
          .style('fill', function(_d) { return avatar(_d); })
          .style('background-image', 'url(' + avatarBackgroundPath + ')')
          .style('background-size', 'cover')
          .style('opacity', 1);

        var tooltip = container.append('div')
          .attr('class', 'matrix-tooltip')
          .style('top', parseInt(selection.attr('cy'), 10) + 45 + 'px')
          .style('left', parseInt(selection.attr('cx'), 10) - 120 + 'px');

        // The tooltip starts out hidden while inserting data...
        tooltip.style('opacity', 0);
        var fullName = d.firstName ? d.firstName + ' ' + d.lastName : d.lastName;
        tooltip.append('h4')
          .attr('class', config.demoMode.blur ? 'demo-mode-blur' : 'matrix-tooltip-header')
          .text(fullName);
        var table = tooltip.append('table').attr('class', 'matrix-tooltip-table');
        var daysSinceRow = table.append('tr');
        daysSinceRow.append('td').attr('class', 'matrix-tooltip-label').text('Days since bCourses course site viewed');
        daysSinceRow.append('td').attr('class', 'matrix-tooltip-value').text(displayValue(d, 'analytics.lastActivity'));
        var yAxisRow = table.append('tr');
        yAxisRow.append('td').text(yAxisName);
        yAxisRow.append('td').attr('class', 'matrix-tooltip-value').text(displayValue(d, yAxisMeasure));

        // ...and transitions to visible.
        tooltip.transition(d3.transition().duration(100).ease(d3.easeLinear))
          .on('start', function() {
            tooltip.style('display', 'block');
          })
          .style('opacity', 1);
      };

      var onDotDeselected = function() {
        d3.select(this).attr('r', '9')
          .style('fill', '#8bbdda')
          .style('opacity', 0.66)
          .style('stroke-width', 0);

        container.select('.matrix-tooltip')
          .transition(d3.transition().duration(500))
          .on('end', function() {
            this.remove();
          })
          .style('opacity', 0);
      };

      dot.on('mouseover', onDotSelected);
      dot.on('mouseout', onDotDeselected);
    };

    var yAxisMeasure = function() {
      return $location.search().yAxis || 'analytics.currentScore';
    };

    var partitionPlottableStudents = function(students) {
      return _.partition(students, function(student) {
        return _.isFinite(_.get(student, 'analytics.lastActivity.percentile')) && _.isFinite(_.get(student, yAxisMeasure() + '.percentile'));
      });
    };

    /**
     * Draw scatterplot graph.
     *
     * @param  {Student[]}      students        Members of group, cohort or whatever
     * @param  {Function}       goToUserPage    Browser redirects to student profile page
     * @param  {Function}       callback        Standard callback
     * @return {void}
     */
    var scatterplotRefresh = function(students, goToUserPage, callback) {
      // Pass along a subset of students that have useful data.
      var partitions = partitionPlottableStudents(students);
      drawScatterplot(partitions[0], yAxisMeasure(), goToUserPage);
      callback(yAxisMeasure, partitions[1]);
    };

    return {
      partitionPlottableStudents: partitionPlottableStudents,
      scatterplotRefresh: scatterplotRefresh,
      showUnitsChart: showUnitsChart
    };

  });

}(window.angular));
