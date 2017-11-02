(function(angular) {

  'use strict';

  angular.module('boac').controller('CohortController', function(cohortFactory, authService, $scope, $state, $stateParams) {

    var displayCohort = function(cohort) {
      $scope.cohort = cohort.data;
      $scope.selectedTab = 'list';
      $scope.cohort.sortBy = 'name';

      var partitionedMembers = _.partition(cohort.data.members, function(member) {
        return _.isFinite(_.get(member, 'analytics.pageViews'));
      });
      var membersWithData = partitionedMembers[0];
      $scope.membersWithoutData = partitionedMembers[1];

      var svg;

      function x(d) { return d.analytics.pageViews; }
      function y(d) {
        var assignmentsOnTime = _.get(d, 'analytics.assignmentsOnTime');
        // Points with no y-axis data are plotted below the x-axis.
        return _.isFinite(assignmentsOnTime) ? assignmentsOnTime : -10;
      }
      function key(d) { return d.uid; }

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

      svg = d3.select('#scatterplot')
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
        .text('Assignments on time');

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
        .data(membersWithData, key)
        .enter().append('circle')
        .attr('class', 'dot')
        .style('fill', function(d) { return avatar(d); })
        .style('stroke-width', 5)
        .style('stroke', '#ccc')
        .attr('cx', function(d) { return xScale(x(d)); })
        .attr('cy', function(d) { return yScale(y(d)); })
        .attr('r', '30');

      // Add a title.
      var displayValue = function(d, prop) {
        var value = _.get(d, prop);
        if (!_.isFinite(value)) {
          return 'No data';
        }
        return _.round(value, 1) + ' percentile';
      };

      dot.append('title')
        .text(function(d) {
          return d.name.concat(
            '\nPage views: ',
            displayValue(d, 'analytics.pageViews'),
            '\nAssignments on time: ',
            displayValue(d, 'analytics.assignmentsOnTime')
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
    };

    var loadCohort = authService.authWrap(function() {
      cohortFactory.getCohortDetails($stateParams.code).then(
        displayCohort,
        function() {
          $scope.errored = true;
        }
      );
    });

    loadCohort();
  });
}(window.angular));
