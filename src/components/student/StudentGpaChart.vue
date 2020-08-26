<template>
  <highcharts
    :id="'student-chart-gpa-container-' + student.uid"
    ref="studentGpaChart"
    :options="gpaChartOptions"
    aria-hidden="true">
  </highcharts>
</template>

<script>
import _ from 'lodash'

export default {
  name: 'StudentGpaChart',
  props: {
    student: Object,
    width: String
  },
  data: () => ({
    gpaChartOptions: {
      title: {
        text: ''
      },
      credits: false,
      chart: {
        width: null,
        height: 30,
        type: 'area',
        margin: [2, 0, 2, 0],
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
          data: []
        }
      ],
      colors: ['#4a90e2']
    }
  }),
  mounted() {
    this.renderGpaToChart()
  },
  methods: {
    generateGpaDataSeries() {
      var series = []
      var i = 0
      _.eachRight(this.student.termGpa, term => {
        series.push({
          x: i,
          y: term.gpa
        })
        i++
      })
      if (series.length) {
        var lastElement = series[series.length - 1]
        var fillColor = lastElement.y < 2 ? '#d0021b' : '#3b7ea5'
        lastElement.marker = {
          fillColor: fillColor,
          radius: 5
        }
      }
      return series
    },
    renderGpaToChart() {
      this.gpaChartOptions.series[0].data = this.generateGpaDataSeries()
      this.gpaChartOptions.chart.width =
        this.width || this.$refs.studentGpaChart.$el.parentNode.clientWidth - 5
    }
  }
}
</script>
