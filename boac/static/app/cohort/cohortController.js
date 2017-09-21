(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(cohortFactory, $scope, $state, $stateParams) {

    cohortFactory.getCohortDetails($stateParams.code).then(function(cohort) {
      $scope.cohort = cohort.data;

      var svg;

      function x(d) { return d.analytics.pageViews; }
      function y(d) { return d.analytics.assignmentsOnTime; }
      function key(d) { return d.uid; }

      var margin = {top: 19.5, right: 19.5, bottom: 25, left: 30};
      var width = 960 - margin.right - margin.left;
      var height = 546 - margin.top - margin.bottom;

      var xScale = d3.scale.linear().domain([0, 100]).range([0, width]).nice();
      var yScale = d3.scale.linear().domain([0, 100]).range([height, 0]).nice();

      var xAxis = d3.svg.axis()
        .scale(xScale)
        .orient('bottom')
        .ticks(10, d3.format(',d'))
        .tickSize(-height);

      var yAxis = d3.svg.axis()
        .scale(yScale)
        .orient('left')
        .ticks(10, d3.format(',d'))
        .tickSize(-width);

      function position(dot) {
        dot.attr('cx', function(d) { return xScale(x(d)); })
          .attr('cy', function(d) { return yScale(y(d)); })
          .attr('r', '30');
      }

      function zoom() {
        svg.select('.x.axis').call(xAxis);
        svg.select('.y.axis').call(yAxis);
        svg.selectAll('.dot').call(position);
      }

      var zoomScaled = d3.behavior.zoom()
        .x(xScale)
        .y(yScale)
        .scaleExtent([1, 10])
        .on('zoom', zoom);

      svg = d3.select('#scatterplot')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .call(zoomScaled);

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
        .text('Assignments on time');

      var defs = svg.append('svg:defs');

      defs.append('svg:pattern')
        .attr('id', 'grump_avatar')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('patternContentUnits', 'objectBoundingBox')
        .append('svg:image')
        .attr('xlink:href', '/static/app/shared/avatar-female.png')
        .attr('width', 1)
        .attr('height', 1)
        .attr('preserveAspectRatio', 'none');

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
        .attr('height', height + 70);

      // Add the year label; the value is set on transition.
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
        .data(cohort.data.members, key)
        .enter().append('circle')
        .attr('class', 'dot')
        .style('fill', 'url(#grump_avatar)')
        .style('stroke-width', 5)
        .style('stroke', '#ccc')
        .call(position);

      // Add a title.
      dot.append('title')
        .text(function(d) {
          return d.name.concat(
            '\nPage views: ',
            _.round(d.analytics.pageViews, 1),
            ' percentile',
            '\nAssignments on time: ',
            _.round(d.analytics.assignmentsOnTime, 1),
            ' percentile'
          );
        });

      dot.on('mouseover', function() {
        this.parentNode.appendChild(this);
        d3.select(this).style('stroke', '#ada');
      });

      dot.on('mouseout', function() {
        d3.select(this).style('stroke', '#ccc');
      });

      dot.on('click', function(d) {
        $state.go('user', {uid: d.uid});
      });
    });
  });

}(window.angular));
