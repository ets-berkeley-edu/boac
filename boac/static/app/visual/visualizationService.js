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

  angular.module('boac').service('visualizationService', function(status, utilService) {

    var showUnitsChart = function(cumulativeUnits, currentEnrolledUnits) {
      var tooltipBodyFormat = '<div class="profile-tooltip-content">' +
                              '<div class="profile-tooltip-row">' +
                              '<div class="profile-tooltip-swatch" style="background-color:#aec9eb"></div>' +
                              '<div class="profile-tooltip-label">Units Completed</div>' +
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
          type: 'column'
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
        unitsChartOptions.chart.width = angular.element(document.querySelector('#profile-units-chart-container'))[0].parentNode.clientWidth;
        Highcharts.chart('profile-units-chart-container', unitsChartOptions);
      });
    };

    var showGpaChart = function(element, gpaTerms, width) {
      var seriesData = [];
      var i = 0;
      _.eachRight(gpaTerms, function(term) {
        seriesData.push({
          x: i,
          y: term.gpa
        });
        i++;
      });

      if (seriesData.length) {
        var fillColor = seriesData[seriesData.length - 1].y < 2 ? '#d0021b' : '#3b7ea5';
        seriesData[seriesData.length - 1].marker = {
          fillColor: fillColor,
          radius: 5
        };
      }

      var gpaChartOptions = {
        title: {
          text: ''
        },
        credits: false,
        chart: {
          renderTo: element,
          width: width,
          height: 40,
          type: 'area',
          margin: [
            2,
            0,
            2,
            0
          ],
          style: {
            overflow: 'visible'
          },
          skipClone: true
        },
        yAxis: {
          endOnTick: false,
          startOnTick: false,
          labels: {
            enabled: false
          },
          title: {
            text: null
          },
          softMin: 1.9,
          plotLines: [
            {
              color: '#888',
              dashStyle: 'dot',
              width: 1,
              value: 2
            }
          ],
          tickPositions: []
        },
        xAxis: {
          labels: {
            enabled: false
          },
          title: {
            text: null
          },
          startOnTick: false,
          endOnTick: false,
          tickPositions: [],
          visible: false
        },
        legend: {
          enabled: false
        },
        tooltip: {
          enabled: false
        },
        plotOptions: {
          line: {
            states: {
              hover: {
                enabled: false
              }
            }
          },
          series: {
            marker: {
              radius: 0
            }
          }
        },
        series: [
          {
            type: 'line',
            data: seriesData
          }
        ],
        colors: [ '#4a90e2' ]
      };

      setTimeout(function() {
        return new Highcharts.Chart(gpaChartOptions, 0);
      });
    };

    var formatForDisplay = function(prop) {
      if (prop === 'analytics.currentScore') {
        return 'Assignment grades';
      }
      if (prop === 'analytics.lastActivity') {
        return 'Days since bCourses site viewed';
      }
      if (prop === 'cumulativeGPA') {
        return 'Cumulative GPA';
      }
      if (prop.startsWith('termGpa')) {
        var termId = prop.slice(-4);
        return utilService.termNameForSisId(termId) + ' GPA';
      }
      return '';
    };

    var isGpaProp = function(prop) {
      return (prop === 'cumulativeGPA') || prop.startsWith('termGpa');
    };

    var getDisplayProperty = function(obj, prop) {
      if (_.has(obj, prop + '.displayPercentile')) {
        return _.get(obj, prop + '.displayPercentile') + ' percentile';
      }
      if (_.has(obj, prop)) {
        return _.get(obj, prop);
      }
      return 'No data';
    };

    var getLabelLower = function(prop) {
      if (prop === 'analytics.currentScore') {
        return 'Low';
      }
      if (prop === 'analytics.lastActivity') {
        return 'Less recent';
      }
      return '';
    };

    var getLabelUpper = function(prop) {
      if (prop === 'analytics.currentScore') {
        return 'High';
      }
      if (prop === 'analytics.lastActivity') {
        return 'More recent';
      }
      return '';
    };

    var getTickFormat = function(prop) {
      return isGpaProp(prop) ? d3.format('.2f') : '';
    };

    var getPlottableProperty = function(obj, prop) {
      if (_.has(obj, prop + '.percentile')) {
        return _.get(obj, prop + '.percentile');
      }
      return _.get(obj, prop);
    };

    var hasPlottableProperty = function(obj, prop) {
      // In the case of cumulative GPA, zero indicates missing data rather than a real zero.
      if (prop === 'cumulativeGPA') {
        return !!getPlottableProperty(obj, prop);
      }
      return _.isFinite(getPlottableProperty(obj, prop));
    };

    var drawScatterplot = function(students, xAxisMeasure, yAxisMeasure, goToUserPage) {
      var svg;

      function x(d) { return getPlottableProperty(d, xAxisMeasure); }
      function y(d) { return getPlottableProperty(d, yAxisMeasure); }
      function key(d) { return d.uid; }

      var classMean = students[0];

      var width = 910;
      var height = 500;

      var xMax = isGpaProp(xAxisMeasure) ? 4 : 100;
      var yMax = isGpaProp(yAxisMeasure) ? 4 : 100;

      var xScale = d3.scaleLinear().domain([0, xMax]).range([0, width]).nice();
      var yScale = d3.scaleLinear().domain([0, yMax]).range([height, 0]).nice();

      var zoomProperties = {
        scale: 1
      };

      var xAxis = d3.axisBottom(xScale)
        .ticks(10)
        .tickFormat(getTickFormat(xAxisMeasure))
        .tickSize(-height);

      var yAxis = d3.axisLeft(yScale)
        .ticks(10)
        .tickFormat(getTickFormat(yAxisMeasure))
        .tickSize(-width);

      var onZoom = function() {
        var transform = d3.event.transform;
        var xNewScale = transform.rescaleX(xScale);
        xAxis.scale(xNewScale);
        svg.select('.x.matrix-axis').call(xAxis);
        var yNewScale = transform.rescaleY(yScale);
        yAxis.scale(yNewScale);
        svg.select('.y.matrix-axis').call(yAxis);
        svg.selectAll('.matrix-quadrant-rect').attr('transform', transform);
        svg.selectAll('.dot')
          .attr('cx', function(d) { return transform.applyX(xScale(x(d))); })
          .attr('cy', function(d) { return transform.applyY(yScale(y(d))); });
        zoomProperties.scale = transform.k;
      };

      var zoom = d3.zoom()
        .scaleExtent([1, 10])
        .translateExtent([[0, 0], [width, height]])
        // Disable zoom events triggered by the mouse wheel.
        .filter(function() { return !event.button && event.type !== 'wheel'; })
        .on('zoom', onZoom);

      var container = d3.select('#matrix-container');

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3.select('#scatterplot')
        .html('')
        .append('svg')
        .attr('class', 'matrix-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('stroke', 1);

      svg.call(zoom);

      zoomProperties.programmaticZoom = function(scale, callback) {
        svg.transition().duration(300)
          .call(zoom.scaleBy, scale)
          .on('end', callback);
      };

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', xScale(x(classMean)))
        .attr('height', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#fffbda');

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', xScale(x(classMean)))
        .attr('height', height - yScale(y(classMean)))
        .attr('y', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#ffdcda');

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', width - xScale(x(classMean)))
        .attr('height', yScale(y(classMean)))
        .attr('x', xScale(x(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#e6ffda');

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', width - xScale(x(classMean)))
        .attr('height', height - yScale(y(classMean)))
        .attr('x', xScale(x(classMean)))
        .attr('y', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#fffbda');

      svg.append('g')
        .attr('class', 'x matrix-axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

      // Add the y-axis.
      svg.append('g')
        .attr('class', 'y matrix-axis')
        .call(yAxis);

      var defs = svg.append('svg:defs');

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
        var photoUri = null;
        if (d.isClassMean) {
          photoUri = '/static/app/course/class-mean-avatar.svg';
        } else {
          photoUri = status.inDemoMode ? avatarBackgroundPath : '/api/student/' + d.uid + '/photo';
        }
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
        .attr('clip-path', 'url(#clip-inner)');

      var dot = dotGroup.attr('class', 'dots')
        .selectAll('.dot')
        .data(students, key)
        .enter().append('circle')
        .attr('class', function(d) { return d.isClassMean ? 'dot dot-mean' : 'dot dot-student'; })
        .style('fill', function(d) { return d.isClassMean ? avatar(d) : '#8bbdda'; })
        .style('opacity', function(d) { return d.isClassMean ? 1 : 0.66; })
        .style('stroke-width', 0)
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', function(d) { return d.isClassMean ? 22 : 9; });

      // Add x-axis labels.
      svg.append('text')
        .attr('class', 'matrix-axis-title')
        .attr('x', width / 2)
        .attr('y', height + 35)
        .text(formatForDisplay(xAxisMeasure));
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', 0)
        .attr('y', height + 22)
        .text(getLabelLower(xAxisMeasure));
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', width)
        .attr('y', height + 22)
        .text(getLabelUpper(xAxisMeasure));

      // Add y-axis labels, breaking lines to conserve space.
      svg.append('text')
        .attr('class', 'matrix-axis-title')
        .attr('y', -35)
        .attr('x', 0 - (height / 2))
        .attr('transform', 'rotate(-90)')
        .text(formatForDisplay(yAxisMeasure));
      var lowerYText = svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', -10)
        .attr('y', height - 20);
      _.each(getLabelLower(yAxisMeasure).split(' '), function(word) {
        lowerYText.append('tspan')
          .attr('x', -10)
          .attr('dy', 12)
          .text(word);
      });
      var upperYText = svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', 0)
        .attr('y', 0);
      _.each(getLabelUpper(yAxisMeasure).split(' '), function(word) {
        upperYText.append('tspan')
          .attr('x', -10)
          .attr('dy', 12)
          .text(word);
      });
      dot.on('click', function(d) {
        if (!d.isClassMean) {
          goToUserPage(d.uid);
        }
      });

      var onDotSelected = function(d) {
        // Clear any existing tooltips.
        container.selectAll('.matrix-tooltip').remove();

        /*
         * If the dot represents a real student, lift it outside the path-clipped dotGroup so it can
         * overlap the edge of the matrix if need be.
         */
        if (!d.isClassMean) {
          objects.node().appendChild(this);
        }
        // Stroke highlight.
        var selection = d3.select(this);
        selection.attr('r', '45')
          .style('stroke-width', function(_d) { return _d.isClassMean ? 0 : 5; })
          .style('stroke', '#ccc')
          .style('fill', function(_d) { return avatar(_d); })
          .style('background-image', 'url(' + avatarBackgroundPath + ')')
          .style('background-size', 'cover')
          .style('opacity', 1);

        var tooltip = container.append('div')
          .attr('class', 'matrix-tooltip')
          .style('top', parseInt(selection.attr('cy'), 10) + 80 + 'px')
          .style('left', parseInt(selection.attr('cx'), 10) - 120 + 'px');

        // The tooltip starts out hidden while inserting data...
        tooltip.style('opacity', 0);
        var headerOuter = tooltip.append('div').attr('class', 'matrix-tooltip-header-outer');
        var fullName = d.firstName ? d.firstName + ' ' + d.lastName : d.lastName;
        headerOuter.append('h4')
          .attr('class', status.inDemoMode ? 'demo-mode-blur' : 'matrix-tooltip-header')
          .text(fullName);
        _.each(d.majors, function(major) {
          headerOuter.append('div')
            .attr('class', 'matrix-tooltip-major')
            .text(major);
        });
        var table = tooltip.append('table').attr('class', 'matrix-tooltip-table');
        var daysSinceRow = table.append('tr');
        daysSinceRow.append('td').attr('class', 'matrix-tooltip-label').text(formatForDisplay(xAxisMeasure));
        daysSinceRow.append('td').attr('class', 'matrix-tooltip-value').text(getDisplayProperty(d, xAxisMeasure));
        var yAxisRow = table.append('tr');
        yAxisRow.append('td').attr('class', 'matrix-tooltip-label').text(formatForDisplay(yAxisMeasure));
        yAxisRow.append('td').attr('class', 'matrix-tooltip-value').text(getDisplayProperty(d, yAxisMeasure));

        // ...and transitions to visible.
        tooltip.transition(d3.transition().duration(100).ease(d3.easeLinear))
          .on('start', function() {
            tooltip.style('display', 'block');
          })
          .style('opacity', 1);
      };

      var onDotDeselected = function() {
        // Return the dot to the path-clipped dot group.
        dotGroup.node().appendChild(this);

        d3.select(this)
          .attr('r', function(_d) { return _d.isClassMean ? 22 : 9; })
          .style('fill', function(_d) { return _d.isClassMean ? avatar(_d) : '#8bbdda'; })
          .style('opacity', function(_d) { return _d.isClassMean ? 1 : 0.66; })
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

      return {
        zoomProperties: zoomProperties
      };
    };

    var partitionPlottableStudents = function(xAxisMeasure, yAxisMeasure, students) {
      return _.partition(students, function(student) {
        return hasPlottableProperty(student, xAxisMeasure) && hasPlottableProperty(student, yAxisMeasure);
      });
    };

    /**
     * Draw scatterplot graph.
     *
     * @param  {Student[]}      students        Members of group, cohort or whatever
     * @param  {Object}         meanMetrics     Mean statistics for the scatterplot context
     * @param  {Object}         selectedAxes    Currently selected x-axis and y-axis metrics
     * @param  {Function}       goToUserPage    Browser redirects to student profile page
     * @param  {Function}       callback        Standard callback
     * @return {void}
     */
    var scatterplotRefresh = function(students, meanMetrics, selectedAxes, goToUserPage, callback) {
      // Pass along a subset of students that have useful data.
      var partitions = partitionPlottableStudents(selectedAxes.x, selectedAxes.y, students);
      var plottableStudents = partitions[0];
      if (meanMetrics) {
        // The imaginary mean must be drawn first, so as not to block access to real students.
        plottableStudents.unshift({
          analytics: meanMetrics,
          cumulativeGPA: meanMetrics.gpa.cumulative,
          isClassMean: true,
          lastName: 'Class Average',
          termGpa: meanMetrics.gpa
        });
      }
      var scatterplotProps = drawScatterplot(plottableStudents, selectedAxes.x, selectedAxes.y, goToUserPage);
      callback(partitions[1], scatterplotProps.zoomProperties);
    };

    return {
      formatForDisplay: formatForDisplay,
      getDisplayProperty: getDisplayProperty,
      hasPlottableProperty: hasPlottableProperty,
      partitionPlottableStudents: partitionPlottableStudents,
      scatterplotRefresh: scatterplotRefresh,
      showGpaChart: showGpaChart,
      showUnitsChart: showUnitsChart
    };

  });

}(window.angular));
