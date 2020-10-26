<template>
  <div>
    <div id="matrix-student-performance-header" class="matrix-student-performance-header">
      <h2 class="matrix-header">Student Performance</h2>
    </div>
    <div id="matrix-choose-metrics" class="matrix-choose-metrics">
      <strong>Compare:</strong>
      <select
        id="matrix-choose-metrics-y-axis"
        v-model="selectedAxes.y"
        class="matrix-choose-metrics-select"
        @change="refreshMatrix">
        <option
          v-for="(yAxisName, yAxisValue) in axisLabels"
          :key="yAxisName"
          :value="yAxisValue"
          :disabled="yAxisValue === selectedAxes.x">
          {{ yAxisName }}
        </option>
      </select>
      <select
        id="matrix-choose-metrics-x-axis"
        v-model="selectedAxes.x"
        class="matrix-choose-metrics-select"
        @change="refreshMatrix">
        <option
          v-for="(xAxisName, xAxisValue) in axisLabels"
          :key="xAxisName"
          :value="xAxisValue"
          :disabled="xAxisValue === selectedAxes.y">
          {{ xAxisName }}
        </option>
      </select>
    </div>
    <div id="matrix-container" class="matrix-container">
      <div v-if="plottable" class="matrix-zoom-wrapper">
        Zoom:
        <div class="btn-group">
          <button
            id="btn-matrix-zoom-in"
            type="button"
            class="btn matrix-zoom-button"
            @click="zoomIn"
            @keyup.enter="zoomIn">
            <font-awesome icon="plus" />
            <span class="sr-only">Zoom in</span>
          </button>
          <button
            id="btn-matrix-zoom-out"
            :disabled="zoom.scale === 1"
            type="button"
            class="btn matrix-zoom-button"
            @click="zoomOut"
            @keyup.enter="zoomOut">
            <font-awesome :class="{'matrix-zoom-disabled': zoom.scale === 1}" icon="minus" />
            <span class="sr-only">Zoom out</span>
          </button>
        </div>
      </div>
      <div v-if="plottable" id="scatterplot" class="matrix"></div>
      <div v-if="!$_.isEmpty(studentsWithoutData)" id="cohort-missing-student-data" class="cohort-missing-student-data">
        <h2 class="matrix-header">Missing Student Data</h2>
        <div>For the following students, some results may only provide partial data or information is currently unavailable:</div>
        <table class="missing-student-data-table">
          <thead>
            <tr class="cohort-missing-student-data-header">
              <th class="student-avatar-container" scope="col"></th>
              <th class="cohort-student-bio-container" scope="col"><span class="sr-only">Student Name</span></th>
              <th class="student-column" scope="col">{{ axisLabels[selectedAxes.x] }}</th>
              <th class="student-column" scope="col">{{ axisLabels[selectedAxes.y] }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="student in studentsWithoutData"
              :id="student.uid"
              :key="student.uid"
              :class="{'cohort-list-row-info': featured === student.uid}"
              class="cohort-missing-student-data-row">
              <td class="student-avatar-container">
                <StudentAvatar :student="student" />
              </td>
              <td class="cohort-student-bio-container">
                <div class="flex-container">
                  <div class="flex-container student-name">
                    <router-link
                      :id="`link-to-student-${student.uid}`"
                      :class="{'demo-mode-blur': $currentUser.inDemoMode}"
                      :to="studentRoutePath(student.uid, $currentUser.inDemoMode)">
                      {{ student.lastName + (student.firstName ? ', ' + student.firstName : '') }}
                    </router-link>
                  </div>
                </div>
                <div
                  v-if="student.sid"
                  :class="{'demo-mode-blur': $currentUser.inDemoMode}"
                  class="student-sid">
                  SID: {{ student.sid }}
                </div>
              </td>
              <td class="student-column">
                <span v-if="hasPlottableProperty(student, selectedAxes.x)">
                  {{ getDisplayProperty(student, selectedAxes.x) }}
                </span>
                <span v-if="!hasPlottableProperty(student, selectedAxes.x)" class="sr-only">
                  No data
                </span>
              </td>
              <td class="student-column">
                <span v-if="hasPlottableProperty(student, selectedAxes.y)">
                  {{ getDisplayProperty(student, selectedAxes.y) }}
                </span>
                <span v-if="!hasPlottableProperty(student, selectedAxes.y)" class="sr-only">
                  No data
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="matrix-container"></div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import _ from 'lodash'
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import MatrixUtil from '@/components/matrix/MatrixUtil'
import StudentAvatar from '@/components/student/StudentAvatar'
import Util from '@/mixins/Util'

export default {
  name: 'Matrix',
  components: {
    StudentAvatar
  },
  mixins: [Berkeley, Context, MatrixUtil, Util],
  props: {
    featured: String,
    section: Object
  },
  data: () => ({
    axisLabels: {},
    plottable: true,
    selectedAxes: {
      x: 'analytics.currentScore',
      y: 'cumulativeGPA'
    },
    studentsWithoutData: [],
    zoom: _.noop,
    zoomIn: _.noop,
    zoomOut: _.noop
  }),
  mounted() {
    this.initAxisLabels()
    this.refreshMatrix()
  },
  methods: {
    drawScatterplot(students) {
      var svg

      var xAxisMeasure = this.selectedAxes.x
      var yAxisMeasure = this.selectedAxes.y

      var x = d => this.getPlottableProperty(d, xAxisMeasure)
      var y = d => this.getPlottableProperty(d, yAxisMeasure)
      var key = d => d.uid

      var classMean = students[0]

      var width = 910
      var height = 500

      var xMax = this.isGpaProp(xAxisMeasure) ? 4 : 100
      var yMax = this.isGpaProp(yAxisMeasure) ? 4 : 100

      var xScale = d3
        .scaleLinear()
        .domain([0, xMax])
        .range([0, width])
        .nice()
      var yScale = d3
        .scaleLinear()
        .domain([0, yMax])
        .range([height, 0])
        .nice()

      var zoomProperties = {
        scale: 1
      }

      var xAxis = d3
        .axisBottom(xScale)
        .ticks(10)
        .tickFormat(this.getTickFormat(xAxisMeasure))
        .tickSize(-height)

      var yAxis = d3
        .axisLeft(yScale)
        .ticks(10)
        .tickFormat(this.getTickFormat(yAxisMeasure))
        .tickSize(-width)

      var container = d3.select('#matrix-container')

      var clearTooltips = () => {
        container.selectAll('.matrix-tooltip').remove()
      }

      var onZoom = () => {
        clearTooltips()
        var transform = d3.event.transform
        var xNewScale = transform.rescaleX(xScale)
        xAxis.scale(xNewScale)
        svg.select('.x.matrix-axis').call(xAxis)
        var yNewScale = transform.rescaleY(yScale)
        yAxis.scale(yNewScale)
        svg.select('.y.matrix-axis').call(yAxis)
        svg.selectAll('.matrix-quadrant-rect').attr('transform', transform)
        svg
          .selectAll('.dot')
          .attr('cx', d => transform.applyX(xScale(x(d))))
          .attr('cy', d => transform.applyY(yScale(y(d))))
        zoomProperties.scale = transform.k
      }

      var zoom = d3
        .zoom()
        .scaleExtent([1, 10])
        .translateExtent([[0, 0], [width, height]])
        // Disable zoom events triggered by the mouse wheel.
        .filter(() => !d3.event.button && d3.event.type !== 'wheel')
        .on('zoom', onZoom)

      // Clear any lingering tooltips.
      clearTooltips()

      // We clear the '#scatterplot' div with `html()` in case the current search results are replacing previous results.
      svg = d3
        .select('#scatterplot')
        .html('')
        .append('svg')
        .attr('class', 'matrix-svg')
        .attr('width', width)
        .attr('height', height)
        .attr('stroke', 1)

      svg.call(zoom)

      zoomProperties.programmaticZoom = scale => {
        svg
          .transition()
          .duration(300)
          .call(zoom.scaleBy, scale)
      }

      // Make d3 zoom available to the page.
      this.zoom = zoomProperties
      this.zoomIn = () => zoomProperties.programmaticZoom(2)
      this.zoomOut = () => zoomProperties.programmaticZoom(0.5)

      svg
        .append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', xScale(x(classMean)))
        .attr('height', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#fffbda')

      svg
        .append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', xScale(x(classMean)))
        .attr('height', height - yScale(y(classMean)))
        .attr('y', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#ffdcda')

      svg
        .append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', width - xScale(x(classMean)))
        .attr('height', yScale(y(classMean)))
        .attr('x', xScale(x(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#e6ffda')

      svg
        .append('g')
        .attr('clip-path', 'url(#clip-inner)')
        .append('rect')
        .attr('class', 'matrix-quadrant-rect')
        .attr('width', width - xScale(x(classMean)))
        .attr('height', height - yScale(y(classMean)))
        .attr('x', xScale(x(classMean)))
        .attr('y', yScale(y(classMean)))
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1)
        .attr('fill', '#fffbda')

      svg
        .append('g')
        .attr('class', 'x matrix-axis')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis)

      // Add the y-axis.
      svg
        .append('g')
        .attr('class', 'y matrix-axis')
        .call(yAxis)

      var defs = svg.append('svg:defs')

      defs
        .append('svg:clipPath')
        .attr('id', 'clip-inner')
        .append('svg:rect')
        .attr('id', 'clip-rect-inner')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', width)
        .attr('height', height)

      var avatarBackgroundPath = require('@/assets/avatar-50.png')

      var avatar = d => {
        var avatarId = 'avatar_' + d.uid
        var pattern = defs
          .append('svg:pattern')
          .attr('id', avatarId)
          .attr('width', '100%')
          .attr('height', '100%')
          .attr('patternContentUnits', 'objectBoundingBox')
        var photoUri = null
        if (d.isClassMean) {
          photoUri = require('@/assets/class-mean-avatar.svg')
        } else {
          photoUri = this.$currentUser.inDemoMode
            ? avatarBackgroundPath
            : d.photoUrl
        }
        var avatarImage = pattern
          .append('svg:image')
          .attr('xlink:href', photoUri)
          .attr('width', 1)
          .attr('height', 1)
          .attr('preserveAspectRatio', 'xMidYMid slice')
        avatarImage.on('error', () =>
          avatarImage.attr('xlink:href', avatarBackgroundPath)
        )
        return 'url(#' + avatarId + ')'
      }

      // Add x-axis labels.
      svg
        .append('text')
        .attr('class', 'matrix-axis-title')
        .attr('x', width / 2)
        .attr('y', height + 35)
        .text(this.formatForDisplay(xAxisMeasure))
      svg
        .append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'start')
        .attr('x', 0)
        .attr('y', height + 22)
        .text(this.getLabelLower(xAxisMeasure))
      svg
        .append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', width)
        .attr('y', height + 22)
        .text(this.getLabelUpper(xAxisMeasure))

      // Add y-axis labels, breaking lines to conserve space.
      svg
        .append('text')
        .attr('class', 'matrix-axis-title')
        .attr('y', -35)
        .attr('x', 0 - height / 2)
        .attr('transform', 'rotate(-90)')
        .text(this.formatForDisplay(yAxisMeasure))
      var lowerYText = svg
        .append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', -10)
        .attr('y', height - 20)
      _.each(this.getLabelLower(yAxisMeasure).split(' '), word => {
        lowerYText
          .append('tspan')
          .attr('x', -10)
          .attr('dy', 12)
          .text(word)
      })
      var upperYText = svg
        .append('text')
        .attr('class', 'matrix-axis-label')
        .attr('text-anchor', 'end')
        .attr('x', 0)
        .attr('y', 0)
      _.each(this.getLabelUpper(yAxisMeasure).split(' '), word => {
        upperYText
          .append('tspan')
          .attr('x', -10)
          .attr('dy', 12)
          .text(word)
      })

      var objects = svg
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'none')
        .classed('matrix-svg', true)
        .classed('objects', true)

      objects
        .append('svg:defs')
        .append('svg:clipPath')
        .attr('id', 'clip')
        .append('svg:rect')
        .attr('id', 'clip-rect')
        .attr('x', -55)
        .attr('y', -55)
        .attr('width', width + 110)
        .attr('height', height + 110)

      var dotGroup = objects.append('g').attr('clip-path', 'url(#clip-inner)')

      var dot = dotGroup
        .attr('class', 'dots')
        .selectAll('.dot')
        .data(students, key)
        .enter()
        .append('circle')
        .attr(
          'class',
          d => (d.isClassMean ? 'dot dot-mean' : 'dot dot-student')
        )
        .style('fill', d => (d.isClassMean ? avatar(d) : '#8bbdda'))
        .style('opacity', d => (d.isClassMean ? 1 : 0.66))
        .style('stroke-width', 0)
        .attr('cx', d => xScale(x(d)))
        .attr('cy', d => yScale(y(d)))
        .attr('r', d => (d.isClassMean ? 22 : 9))

      dot.on('click', d => {
        if (!d.isClassMean) {
          this.$router.push(this.studentRoutePath(d.uid, this.$currentUser.inDemoMode))
        }
      })

      var onDotDeselected = (d, element, isProgrammatic) => {
        if (isProgrammatic !== true) {
          element = d3.event.currentTarget
        }

        // Return the dot to the path-clipped dot group.
        dotGroup.node().appendChild(element)

        d3.select(element)
          .attr('r', _d => (_d.isClassMean ? 22 : 9))
          .style('fill', _d => (_d.isClassMean ? avatar(_d) : '#8bbdda'))
          .style('opacity', _d => (_d.isClassMean ? 1 : 0.66))
          .style('stroke-width', 0)

        var tooltip = container.select('.matrix-tooltip')
        tooltip
          .transition(d3.transition().duration(500))
          .on('end', () => tooltip.remove())
          .style('opacity', 0)
      }

      // The "featured" UID passed in as a URL param, if any, will start out selected.
      var getFeaturedStudent = () => {
        var featuredData
        var featuredElement
        var featuredUid = this.featured
        if (featuredUid) {
          dot.each(function(d) {
            if (d.uid === featuredUid) {
              featuredData = d
              featuredElement = this
            }
          })
        }
        return [featuredData, featuredElement]
      }

      var onDotSelected = (d, element, isProgrammatic) => {
        if (isProgrammatic !== true) {
          element = d3.event.currentTarget
        }
        // Clear any existing selections and tooltips.
        var featuredStudent = getFeaturedStudent()
        if (featuredStudent[0]) {
          onDotDeselected(featuredStudent[0], featuredStudent[1], true)
        }
        clearTooltips()
        /*
         * If the dot represents a real student, lift it outside the path-clipped dotGroup so it can
         * overlap the edge of the matrix if need be.
         */
        if (!d.isClassMean) {
          objects.node().appendChild(element)
        }
        // Stroke highlight.
        var selection = d3.select(element)
        selection
          .attr('r', '45')
          .style('stroke-width', _d => (_d.isClassMean ? 0 : 5))
          .style('stroke', '#ccc')
          .style('fill', _d => avatar(_d))
          .style('background-image', 'url(' + avatarBackgroundPath + ')')
          .style('background-size', 'cover')
          .style('opacity', 1)

        var tooltip = container
          .append('div')
          .attr('class', 'matrix-tooltip')
          .style('top', parseInt(selection.attr('cy'), 10) + 80 + 'px')
          .style('left', parseInt(selection.attr('cx'), 10) - 120 + 'px')

        // The tooltip starts out hidden while inserting data...
        tooltip.style('opacity', 0)
        var headerOuter = tooltip
          .append('div')
          .attr('class', 'matrix-tooltip-header-outer')
        var fullName = d.firstName
          ? d.firstName + ' ' + d.lastName
          : d.lastName
        headerOuter
          .append('h4')
          .attr(
            'class',
            this.$currentUser.inDemoMode ? 'demo-mode-blur' : 'matrix-tooltip-header'
          )
          .text(fullName)
        _.each(d.majors, major =>
          headerOuter
            .append('div')
            .attr('class', 'matrix-tooltip-major')
            .text(major)
        )
        var table = tooltip
          .append('table')
          .attr('class', 'matrix-tooltip-table')
        var daysSinceRow = table.append('tr')
        daysSinceRow
          .append('td')
          .attr('class', 'matrix-tooltip-label')
          .text(this.formatForDisplay(xAxisMeasure))
        daysSinceRow
          .append('td')
          .attr('class', 'matrix-tooltip-value')
          .text(this.getDisplayProperty(d, xAxisMeasure))
        var yAxisRow = table.append('tr')
        yAxisRow
          .append('td')
          .attr('class', 'matrix-tooltip-label')
          .text(this.formatForDisplay(yAxisMeasure))
        yAxisRow
          .append('td')
          .attr('class', 'matrix-tooltip-value')
          .text(this.getDisplayProperty(d, yAxisMeasure))

        // ...and transitions to visible.
        tooltip
          .transition(
            d3
              .transition()
              .duration(100)
              .ease(d3.easeLinear)
          )
          .on('start', () => tooltip.style('display', 'block'))
          .style('opacity', 1)
      }

      dot.on('mouseover', onDotSelected)
      dot.on('mouseout', onDotDeselected)

      var featuredStudent = getFeaturedStudent()
      if (featuredStudent[0]) {
        onDotSelected(featuredStudent[0], featuredStudent[1], true)
      }
    },
    formatForDisplay(prop) {
      if (prop === 'analytics.currentScore') {
        return 'Assignment grades'
      }
      if (prop === 'analytics.lastActivity') {
        return 'Days since bCourses site viewed'
      }
      if (prop === 'cumulativeGPA') {
        return 'Cumulative GPA'
      }
      if (prop.startsWith('termGpa')) {
        var termId = prop.slice(-4)
        return this.termNameForSisId(termId) + ' GPA'
      }
      return ''
    },
    isGpaProp(prop) {
      return prop === 'cumulativeGPA' || prop.startsWith('termGpa')
    },
    getDisplayProperty(obj, prop) {
      if (_.has(obj, prop + '.displayPercentile')) {
        return _.get(obj, prop + '.displayPercentile') + ' percentile'
      }
      if (_.has(obj, prop)) {
        const isGPA = prop.toLowerCase().includes('gpa')
        const value = _.get(obj, prop)
        return isGPA ? parseFloat('0' + this.trim(value)).toFixed(3) : value
      }
      return 'No data'
    },
    getLabelLower(prop) {
      if (prop === 'analytics.currentScore') {
        return 'Low'
      }
      if (prop === 'analytics.lastActivity') {
        return 'Less recent'
      }
      return ''
    },
    getLabelUpper(prop) {
      if (prop === 'analytics.currentScore') {
        return 'High'
      }
      if (prop === 'analytics.lastActivity') {
        return 'More recent'
      }
      return ''
    },
    getTickFormat(prop) {
      return this.isGpaProp(prop) ? d3.format('.2f') : ''
    },
    initAxisLabels() {
      let metrics = [
        'analytics.currentScore',
        'analytics.lastActivity',
        'cumulativeGPA'
      ]
      var lastTermId = this.previousSisTermId(this.$config.currentEnrollmentTermId)
      var previousTermId = this.previousSisTermId(lastTermId)
      metrics.push('termGpa.' + previousTermId)
      metrics.push('termGpa.' + lastTermId)
      _.each(metrics, metric => {
        this.axisLabels[metric] = this.formatForDisplay(metric)
      })
    },
    refreshMatrix() {
      var partitions = this.partitionPlottableStudents()
      var plottableStudents = partitions[0]
      this.plottable = plottableStudents.length > 0
      this.studentsWithoutData = _.orderBy(partitions[1], [
        'last_name',
        'first_name'
      ])

      if (this.plottable) {
        if (this.section.meanMetrics) {
          // The imaginary mean must be drawn first, so as not to block access to real students.
          plottableStudents.unshift({
            analytics: this.section.meanMetrics,
            cumulativeGPA: this.section.meanMetrics.gpa.cumulative,
            isClassMean: true,
            lastName: 'Class Average',
            termGpa: this.section.meanMetrics.gpa
          })
        }
        this.$nextTick(() => {
          this.drawScatterplot(plottableStudents)
        })
      }
    }
  }
}
</script>

<style>
.cohort-list-row-info {
  background-color: #bee5eb;
  color: #0c5460;
}
.cohort-missing-student-data {
  margin-top: 30px;
}
.cohort-missing-student-data-header {
  font-weight: bold;
  border-bottom: 1px solid #ddd;
}
.cohort-missing-student-data-header th {
  padding: 15px 0 5px;
}
.cohort-missing-student-data-row {
  border-bottom: 1px solid #ddd;
}
.cohort-missing-student-data-row td {
  padding: 5px 0;
  margin-bottom: 5px;
}
.matrix {
  border: 1px solid #999;
  height: 500px;
  margin-bottom: 60px;
  width: 910px;
}
.matrix .dot {
  stroke: #000;
}
.matrix .dot-mean {
  cursor: auto;
}
.matrix .dot-student {
  cursor: pointer;
}
.matrix .overlay {
  fill: none;
  pointer-events: all;
  cursor: ew-resize;
}
.matrix-axis path,
.matrix-axis line {
  fill: none;
  stroke: rgba(0, 0, 0, 0.1);
  shape-rendering: crispEdges;
}
.matrix-axis-title {
  font-size: 16px;
  font-weight: 200;
  letter-spacing: 0.075em;
  text-anchor: middle;
  text-transform: uppercase;
  stroke: #999;
}
.matrix-axis-label {
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.075em;
  text-transform: uppercase;
}
.matrix-choose-metrics {
  font-size: 14px;
}
.matrix-choose-metrics-select {
  display: inline-block;
  margin: 0 5px;
}
.matrix-container {
  margin: 0 10px 100px 40px;
  margin-bottom: 100px;
  position: relative;
  width: 910px;
}
.matrix-header {
  font-size: 18px;
}
.matrix-outer {
  margin-left: 20px;
}
.matrix-student-performance-header {
  margin: 5px 20px 10px 0;
}
.matrix-svg {
  overflow: visible !important;
}
.matrix-tooltip {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #666;
  line-height: 1.4em;
  opacity: 1;
  padding: 5px 10px;
  position: absolute;
  text-align: left;
  width: 240px;
  z-index: 1;
}
.matrix-tooltip-header {
  color: #49b;
  font-size: 14px;
  font-weight: bold;
  margin: 0 0 5px;
}
.matrix-tooltip-header-outer {
  margin: 5px 20px 10px 0;
}
.matrix-tooltip-major {
  color: #999;
  font-size: 12px;
  line-height: 1.3em;
  margin: 0;
}
.matrix-tooltip-table td {
  font-size: 12px;
  line-height: 1.3;
}
.matrix-tooltip-label {
  padding: 0 10px 2px 0;
}
.matrix-tooltip-value {
  font-weight: bold;
  padding: 0 0 2px 0;
  vertical-align: top;
  white-space: nowrap;
}
.matrix-zoom-button {
  border: 1px solid #ccc;
  height: 30px;
  padding: 0;
  width: 30px;
}
.matrix-zoom-disabled {
  color: #ccc;
}
.matrix-zoom-wrapper {
  margin-bottom: 5px;
  text-align: right;
}
.missing-student-data-table {
  width: 100%;
}
.student-avatar-container {
  align-items: center;
  display: flex;
  flex: 0 0 60px;
}
</style>
