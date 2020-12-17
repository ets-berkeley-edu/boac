<template>
  <div v-if="options">
    <highcharts
      :id="`student-chart-gpa-container-${student.uid}`"
      :options="options"
    />
  </div>
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
      default: undefined,
      required: false,
      type: Number
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
          accessibility: {
            description: `${term.gpa} GPA`
          },
          marker: {
            enabled: true
          },
          x: i,
          y: term.gpa
        })
        i++
      })
      if (series.length) {
        const lastElement = series[series.length - 1]
        const fillColor = lastElement.y < 2 ? '#d0021b' : '#3b7ea5'
        lastElement.marker = {
          enabled: true,
          fillColor: fillColor,
          radius: 5
        }
      }
      return series
    },
    getOptions() {
      return {
        accessibility: {
          description: this.chartDescription,
          enabled: true,
          keyboardNavigation: {
            enabled: true
          }
        },
        title: {
          style: {display: 'none'},
          text: this.chartDescription,
          useHTML: true
        },
        credits: false,
        chart: {
          height: 50,
          type: 'area',
          width: this.width
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
                enabled: true
              }
            }
          },
          series: {
            marker: {
              enabled: true,
              radius: 0
            }
          }
        },
        series: [
          {
            accessibility: {
              description: this.chartDescription,
              enabled: true,
              keyboardNavigation: {
                enabled: true
              }
            },
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
