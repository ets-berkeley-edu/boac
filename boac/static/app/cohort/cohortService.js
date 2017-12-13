(function(angular) {

  'use strict';

  angular.module('boac').service('cohortService', function(cohortFactory) {

    var drawScatterplot = function(students, goToUserPage, yAxisMeasure) {
      var svg;

      function x(d) { return d.analytics.pageViews; }
      function y(d) {
        var yValues = _.get(d, yAxisMeasure);
        // Points with no y-axis data are plotted below the x-axis.
        return _.isFinite(yValues) ? yValues : -10;
      }
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
          svg.select('.x.axis').call(xAxis);

          var yNewScale = transform.rescaleY(yScale);
          yAxis.scale(yNewScale);
          svg.select('.y.axis').call(yAxis);

          svg.selectAll('.dot')
            .attr('cx', function(d) { return transform.applyX(xScale(x(d))); })
            .attr('cy', function(d) { return transform.applyY(yScale(y(d))); });
        });

      var container = d3.select('#cohort-matrix-container');

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3.select('#scatterplot')
        .html('')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(zoom);

      // Add the x-axis.
      svg.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

      // Add the y-axis.
      svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis);

      // Add an x-axis label.
      svg.append('text')
        .attr('class', 'x label')
        .attr('text-anchor', 'end')
        .attr('x', width)
        .attr('y', height - 6)
        .text('Page views');

      // Add a y-axis label.
      svg.append('text')
        .attr('class', 'y label')
        .attr('text-anchor', 'end')
        .attr('y', 6)
        .attr('dy', '.75em')
        .attr('transform', 'rotate(-90)')
        .text(yAxisName);

      var defs = svg.append('svg:defs');

      function avatar(d) {
        var avatarId = 'avatar_' + d.uid;
        defs.append('svg:pattern')
          .attr('id', avatarId)
          .attr('width', '100%')
          .attr('height', '100%')
          .attr('patternContentUnits', 'objectBoundingBox')
          .append('svg:image')
          .attr('xlink:href', d.avatar_url)
          .attr('width', 1)
          .attr('height', 1)
          .attr('preserveAspectRatio', 'none');
        return 'url(#' + avatarId + ')';
      }

      svg.append('rect')
        .attr('width', width)
        .attr('height', height);

      var objects = svg.append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .classed('objects', true);

      objects.append('svg:defs')
        .append('svg:clipPath')
        .attr('id', 'clip')
        .append('svg:rect')
        .attr('id', 'clip-rect')
        .attr('x', -35)
        .attr('y', -35)
        .attr('width', width + 70)
        .attr('height', height + 120);

      svg.append('text')
        .attr('class', 'sample label')
        .attr('text-anchor', 'end')
        .attr('y', height - 24)
        .attr('x', width)
        .text('Student Performance Quadrant');

      objects.append('svg:line')
        .classed('axisLine hAxisLine', true)
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', width)
        .attr('y2', 0)
        .attr('transform', 'translate(0,' + height + ')');

      objects.append('svg:line')
        .classed('axisLine vAxisLine', true)
        .attr('x1', 0)
        .attr('y1', 0)
        .attr('x2', 0)
        .attr('y2', height);

      var dotGroup = objects.append('g')
        .attr('clip-path', 'url(#clip)');

      var dot = dotGroup.attr('class', 'dots')
        .selectAll('.dot')
        .data(students, key)
        .enter().append('circle')
        .attr('class', 'dot')
        .style('fill', function(d) { return avatar(d); })
        .style('stroke-width', 5)
        .style('stroke', '#ccc')
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', '30');

      var displayValue = function(d, prop) {
        var value = _.get(d, prop);
        if (!_.isFinite(value)) {
          return 'No data';
        }
        return _.round(value, 1) + '%';
      };

      dot.on('click', function(d) {
        goToUserPage(d.uid);
      });

      var onDotSelected = function(d) {
        // Clear any existing tooltips.
        container.selectAll('.cohort-matrix-tooltip').remove();

        // Move dot to front.
        this.parentNode.appendChild(this);
        // Stroke highlight.
        var selection = d3.select(this);
        selection.attr('r', '50')
          .style('stroke', '#ada');

        var tooltip = container.append('div')
          .attr('class', 'cohort-matrix-tooltip')
          .style('top', parseInt(selection.attr('cy'), 10) + 30 + 'px')
          .style('left', parseInt(selection.attr('cx'), 10) - 100 + 'px');

        // The tooltip starts out hidden while inserting data...
        tooltip.style('opacity', 0);
        tooltip.append('h4').attr('class', 'cohort-matrix-tooltip-header').text(d.firstName + ' ' + d.lastName);
        var table = tooltip.append('table').attr('class', 'cohort-matrix-tooltip-table');
        var pageViewsRow = table.append('tr');
        pageViewsRow.append('td').text('Page views');
        pageViewsRow.append('td').attr('class', 'cohort-matrix-tooltip-value').text(displayValue(d, 'analytics.pageViews'));
        var yAxisRow = table.append('tr');
        yAxisRow.append('td').text(yAxisName);
        yAxisRow.append('td').attr('class', 'cohort-matrix-tooltip-value').text(displayValue(d, yAxisMeasure));

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

        container.select('.cohort-matrix-tooltip')
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
      if (cohort.label === 'Intensive') {
        return callback('Sorry, \'Intensive\' is a reserved name. Please choose a different name.');
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

    return {
      drawScatterplot: drawScatterplot,
      validateCohortLabel: validateCohortLabel
    };

  });
}(window.angular));
