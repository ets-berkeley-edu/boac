<template>
  <highcharts
    v-if="options"
    :id="`student-chart-gpa-container-${student.uid}`"
    ref="studentGpaChart"
    :options="options"
  />
</template>

<script>
export default {
  name: 'StudentGpaChart',
  props: {
    chartDescription: {
      required: true,
      type: String
    },
    student: {
      required: true,
      type: Object
    },
    width: {
      required: true,
      type: String
    }
  },
  data: () => ({
    options: undefined
  }),
  mounted() {
    this.options = this.getOptions()
  },
  methods: {
    generateGpaDataSeries() {
      const series = []
      let i = 0
      this.$_.eachRight(this.student.termGpa, term => {
        series.push({
          x: i,
          y: term.gpa
        })
        i++
      })
      if (series.length) {
        const lastElement = series[series.length - 1]
        const fillColor = lastElement.y < 2 ? '#d0021b' : '#3b7ea5'
        lastElement.marker = {
          fillColor: fillColor,
          radius: 5
        }
      }
      return series
    },
    getOptions() {
      return {
        accessibility: {
          enabled:true,
          keyboardNavigation: {
            enabled: true
          },
          point: {
            valueDescriptionFormat: '{index}. {point.name}, {point.y}.'
          }
        },
        title: {
          text: ''
        },
        credits: false,
        chart: {
          height: 30,
          margin: [2, 0, 2, 0],
          skipClone: true,
          style: {
            overflow: 'visible'
          },
          type: 'area',
          width: undefined
        },
        yAxis: {
          accessibility: {
            description: 'GPA',
            enabled: true
          },
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
          accessibility: {
            description: 'Time',
            enabled: true
          },
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
          accessibility: {
            description: this.chartDescription,
            enabled: true,
            keyboardNavigation: {
              enabled: true
            },
            pointDescriptionFormatter: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
          },
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
            data: this.generateGpaDataSeries()
          }
        ],
        colors: ['#4a90e2']
      }
    }
  }
}
</script>
