<template>
  <highcharts
    v-if="options"
    :id="`student-chart-gpa-container-${student.uid}`"
    v-highchartsA11y
    :options="options"
  />
</template>

<script setup>
import {eachRight, first, get, last} from 'lodash'
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
  const maximumTerm = get(first(props.student.termGpa), 'termName')
  const minimumTerm = get(last(props.student.termGpa), 'termName')
  options.value = {
    accessibility: {
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
        enabled: true,
        rangeDescription: 'Range: 0 to 5'
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
        description: 'academic terms',
        enabled: true,
        rangeDescription: `Range: ${minimumTerm} to ${maximumTerm}`
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
