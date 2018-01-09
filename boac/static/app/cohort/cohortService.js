(function(angular) {

  'use strict';

  angular.module('boac').service('cohortService', function(cohortFactory) {

    var drawScatterplot = function(students, yAxisMeasure, goToUserPage) {
      var svg;

      function x(d) { return d.analytics.pageViews; }
      function y(d) { return _.get(d, yAxisMeasure); }
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
          svg.select('.x.cohort-matrix-axis').call(xAxis);

          var yNewScale = transform.rescaleY(yScale);
          yAxis.scale(yNewScale);
          svg.select('.y.cohort-matrix-axis').call(yAxis);

          svg.select('.cohort-matrix-gradient-rect').attr('transform', transform);

          svg.selectAll('.dot')
            .attr('cx', function(d) { return transform.applyX(xScale(x(d))); })
            .attr('cy', function(d) { return transform.applyY(yScale(y(d))); });
        });

      var container = d3.select('#cohort-matrix-container');

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3.select('#scatterplot')
        .html('')
        .append('svg')
        .attr('class', 'cohort-matrix-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('stroke', 1)
        .call(zoom);

      svg.append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'cohort-matrix-gradient-rect')
        .attr('fill', 'url(#cohort-matrix-background-gradient)');

      svg.append('g')
        .attr('class', 'x cohort-matrix-axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis);

      // Add the y-axis.
      svg.append('g')
        .attr('class', 'y cohort-matrix-axis')
        .call(yAxis);

      var defs = svg.append('svg:defs');

      var linearGradient = defs.append('linearGradient')
        .attr('id', 'cohort-matrix-background-gradient')
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

      function avatar(d) {
        var avatarId = 'avatar_' + d.uid;
        var pattern = defs.append('svg:pattern')
          .attr('id', avatarId)
          .attr('width', '100%')
          .attr('height', '100%')
          .attr('patternContentUnits', 'objectBoundingBox');
        var avatarImage = pattern.append('svg:image')
          .attr('xlink:href', '/api/user/' + d.uid + '/photo')
          .attr('width', 1)
          .attr('height', 1)
          .attr('preserveAspectRatio', 'xMidYMid slice');
        avatarImage.on('error', function() {
          avatarImage.attr('xlink:href', '/static/app/shared/avatar-50.png');
        });
        return 'url(#' + avatarId + ')';
      }

      var objects = svg.append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .classed('cohort-matrix-svg', true)
        .classed('objects', true);

      objects.append('svg:defs')
        .append('svg:clipPath')
        .attr('id', 'clip')
        .append('svg:rect')
        .attr('id', 'clip-rect')
        .attr('x', -35)
        .attr('y', -35)
        .attr('width', width + 70)
        .attr('height', height + 70);

      var dotGroup = objects.append('g')
        .attr('clip-path', 'url(#clip)');

      var dot = dotGroup.attr('class', 'dots')
        .selectAll('.dot')
        .data(students, key)
        .enter().append('circle')
        .attr('class', 'dot')
        .style('fill', function(d) { return avatar(d); })
        .style('background-image', 'url(/static/app/shared/avatar-50.png)')
        .style('background-size', 'cover')
        .style('stroke-width', 5)
        .style('stroke', '#ccc')
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', '30');

      // Add an x-axis label.
      svg.append('text')
        .attr('class', 'cohort-matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', 0)
        .attr('y', height + 30)
        .text('Page views');

      // Add a y-axis label.
      svg.append('text')
        .attr('class', 'cohort-matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', -height)
        .attr('y', -20)
        .attr('transform', 'rotate(-90)')
        .text(yAxisName);

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

    var getSelected = function(filterOptions, property) {
      return _.map(_.filter(filterOptions, 'selected'), property);
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
      getSelected: getSelected,
      validateCohortLabel: validateCohortLabel
    };

  });
}(window.angular));
