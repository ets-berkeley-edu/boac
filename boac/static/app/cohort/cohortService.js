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

  angular.module('boac').service('cohortService', function(cohortFactory, config, utilService) {

    var drawScatterplot = function(students, yAxisMeasure, goToUserPage) {
      var svg;

      function x(d) { return d.analytics.pageViews.percentile; }
      function y(d) { return _.get(d, yAxisMeasure).percentile; }
      function key(d) { return d.uid; }

      var yAxisName = 'Assignments on time';
      if (yAxisMeasure === 'analytics.courseCurrentScore') {
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

      var zoom = d3.zoom()
        .scaleExtent([1, 10])
        .translateExtent([[0, 0], [width, height]])
        .on('zoom', function() {
          var transform = d3.event.transform;

          var xNewScale = transform.rescaleX(xScale);
          xAxis.scale(xNewScale);
          svg.select('.x.matrix-axis').call(xAxis);

          var yNewScale = transform.rescaleY(yScale);
          yAxis.scale(yNewScale);
          svg.select('.y.matrix-axis').call(yAxis);

          svg.select('.matrix-gradient-rect').attr('transform', transform);

          svg.selectAll('.dot')
            .attr('cx', function(d) { return transform.applyX(xScale(x(d))); })
            .attr('cy', function(d) { return transform.applyY(yScale(y(d))); });
        });

      var container = d3.select('#matrix-container');

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3.select('#scatterplot')
        .html('')
        .append('svg')
        .attr('class', 'matrix-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('stroke', 1)
        .call(zoom);

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
        var photoUri = d.isClassAverage ? '/static/app/course/class-group-icon.svg' : '/api/user/' + d.uid + '/photo';
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
        .style('fill', function(d) { return avatar(d); })
        .style('background-image', 'url(' + avatarBackgroundPath + ')')
        .style('background-size', 'cover')
        .style('stroke-width', 5)
        .style('stroke', '#ccc')
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', '30');

      // Add an x-axis label.
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', 0)
        .attr('y', height + 30)
        .text('bCourses page views');

      // Add a y-axis label.
      svg.append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', -height)
        .attr('y', -20)
        .attr('transform', 'rotate(-90)')
        .text(yAxisName);

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
        selection.attr('r', '50')
          .style('stroke', '#ada');

        var tooltip = container.append('div')
          .attr('class', 'matrix-tooltip')
          .style('top', parseInt(selection.attr('cy'), 10) + 45 + 'px')
          .style('left', parseInt(selection.attr('cx'), 10) - 120 + 'px');

        // The tooltip starts out hidden while inserting data...
        tooltip.style('opacity', 0);
        var fullName = d.firstName ? d.firstName + ' ' + d.lastName : d.lastName;
        tooltip.append('h4')
          .attr('class', config.demoMode ? 'demo-mode-blur' : 'matrix-tooltip-header')
          .text(fullName);
        var table = tooltip.append('table').attr('class', 'matrix-tooltip-table');
        var pageViewsRow = table.append('tr');
        pageViewsRow.append('td').attr('class', 'matrix-tooltip-label').text('bCourses page views');
        pageViewsRow.append('td').attr('class', 'matrix-tooltip-value').text(displayValue(d, 'analytics.pageViews'));
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
        d3.select(this).attr('r', '30')
          .style('stroke', '#ccc');

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

    var validateCohortLabel = function(cohort, callback) {
      if (_.includes(['Intensive', 'Inactive'], cohort.label)) {
        return callback('Sorry, \'' + cohort.label + '\' is a reserved name. Please choose a different name.');
      }
      var error = null;
      cohortFactory.getMyCohorts().then(function(response) {
        _.each(response.data, function(next) {
          var validate = !cohort.id || cohort.id !== next.id;
          if (validate && cohort.label === next.label) {
            error = 'You have a cohort with this name. Please choose a different name.';
            return false;
          }
        });
      }).then(function() {
        return callback(error);
      });
    };

    var decorateCohortAlerts = function(cohort) {
      if (cohort.alerts && cohort.alerts.length) {
        cohort.alerts = {
          isCohortAlerts: true,
          students: utilService.extendSortableNames(cohort.alerts),
          sortBy: 'sortableName',
          reverse: false
        };
      }
    };

    var loadMyCohorts = function(callback) {
      cohortFactory.getMyCohorts().then(function(cohortsResponse) {
        var myCohorts = [];
        _.each(cohortsResponse.data, function(cohort) {
          decorateCohortAlerts(cohort);
          myCohorts.push(cohort);
        });
        return callback(myCohorts);
      });
    };

    return {
      decorateCohortAlerts: decorateCohortAlerts,
      drawScatterplot: drawScatterplot,
      loadMyCohorts: loadMyCohorts,
      validateCohortLabel: validateCohortLabel
    };

  });
}(window.angular));
