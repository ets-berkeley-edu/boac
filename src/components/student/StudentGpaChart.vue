<template>
  <highcharts
    :id="`student-chart-gpa-container-${student.uid}`"
    :options="{
      accessibility: {
        description: chartDescription,
        enabled: true,
        keyboardNavigation: {
          enabled: true
        }
      },
      title: {
        style: {display: 'none'},
        text: chartDescription,
        useHTML: true
      },
      credits: false,
      chart: {
        height: 50,
        type: 'area',
        width: width
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
          description: chartDescription,
          enabled: true,
          keyboardNavigation: {
            enabled: true
          },
          valueDescriptionFormat: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
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
            description: chartDescription,
            enabled: true,
            keyboardNavigation: {
              enabled: true
            }
          },
          type: 'line',
          data: generateGpaDataSeries()
        }
      ],
      colors: ['#4a90e2']
    }"
  />
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'StudentGpaChart',
  mixins: [Util],
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
  methods: {
    generateGpaDataSeries() {
      const series = []
      let i = 0
      this._eachRight(this.student.termGpa, term => {
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
    }
  }
}
</script>
