<template>
  <highcharts
    v-if="options"
    :id="`student-chart-gpa-container-${student.uid}`"
    :options="options"
  />
</template>

<script setup>
import {eachRight} from 'lodash'
import {onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'

const props = defineProps({
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
})

const options = ref(undefined)

onMounted(() => {
  const currentTheme = useTheme().current.value
  options.value = {
    accessibility: {
      description: props.chartDescription,
      enabled: true,
      keyboardNavigation: {
        enabled: true
      }
    },
    title: {
      style: {display: 'none'},
      text: props.chartDescription,
      useHTML: true
    },
    credits: false,
    chart: {
      height: 50,
      type: 'area',
      width: props.width
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
          color: currentTheme.colors['surface-variant'],
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
        description: props.chartDescription,
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
          description: props.chartDescription,
          enabled: true,
          keyboardNavigation: {
            enabled: true
          }
        },
        type: 'line',
        data: generateGpaDataSeries(currentTheme)
      }
    ],
    colors: [currentTheme.colors.primary]
  }
})

const generateGpaDataSeries = (currentTheme) => {
  const series = []
  let i = 0
  eachRight(props.student.termGpa, term => {
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
    const fillColor = lastElement.y < 2 ? currentTheme.colors.error : currentTheme.colors.primary
    lastElement.marker = {
      enabled: true,
      fillColor: fillColor,
      radius: 5
    }
  }
  return series
}
</script>
