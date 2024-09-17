<template>
  <highcharts
    v-if="options"
    :id="`student-chart-boxplot-container-${numericId}`"
    :options="options"
  />
</template>

<script setup>
import {get, size} from 'lodash'
import {onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'

const props = defineProps({
  chartDescription: {
    required: true,
    type: String
  },
  dataset: {
    required: true,
    type: Object
  },
  numericId: {
    required: true,
    type: String
  }
})

const courseDeciles = get(props.dataset, 'courseDeciles')
const options = ref(undefined)

onMounted(() => {
  options.value = getHighchartsOptions()
})

const getHighchartsOptions = () => {
  const currentTheme = useTheme().current.value
  return {
    accessibility: {
      enabled: true,
      keyboardNavigation: {
        enabled: true
      },
      point: {
        valueDescriptionFormat: '{index}. {point.name}, {point.y}.'
      }
    },
    chart: {
      backgroundColor: 'transparent',
      height: 18,
      inverted: true,
      // This unfortunate negative-margin hack compensates for an apparent Highcharts bug when rendering narrow boxplots.
      margin: [-5, 0, 0, 0],
      type: 'boxplot',
      width: 75
    },
    credits: {
      enabled: false
    },
    legend: {
      enabled: false
    },
    plotOptions: {
      boxplot: {
        accessibility: {
          description: props.chartDescription,
          enabled: true,
          exposeAsGroupOnly: true,
          keyboardNavigation: {
            enabled: true
          },
          valueDescriptionFormat: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
        },
        color: currentTheme.colors['chart-boxplot'],
        enableMouseTracking: false,
        fillColor: currentTheme.colors['chart-boxplot'],
        lineWidth: 1,
        medianColor: currentTheme.colors['chart-boxplot-median'],
        medianWidth: 3,
        whiskerLength: 9,
        whiskerWidth: 1
      }
    },
    series: generateSeriesFromDataset(currentTheme),
    title: {
      text: ''
    },
    tooltip: {
      backgroundColor: currentTheme.colors.surface,
      borderColor: currentTheme.colors['surface-light'],
      borderRadius: 16,
      headerFormat: `
        <div class="align-center boxplot-tooltip-font-family boxplot-tooltip-header d-flex justify-space-between px-3 py-2">
          <div>User Score</div>
          <div class="ml-3 pl-5">${get(props.dataset.student, 'raw') || '&mdash;'}</div>
        </div>
      `,
      hideDelay: 0,
      outside: true,
      padding: 0,
      pointFormat: `
        <div class="boxplot-tooltip-font-family px-3 py-2 w-100">
          <div class="align-center d-flex justify-space-between">
            <div>Maximum</div>
            <div class="ml-3 pl-5">${getCourseDecile(10) || '&mdash;'}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>70th Percentile</div>
            <div class="ml-3 pl-5">${getCourseDecile(7) || '&mdash;'}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>50th Percentile</div>
            <div class="ml-3 pl-5">${getCourseDecile(5) || '&mdash;'}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>30th Percentile</div>
            <div class="ml-3 pl-5">${getCourseDecile(3) || '&mdash;'}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>Minimum</div>
            <div class="ml-3 pl-5">${getCourseDecile(0) || '&mdash;'}</div>
          </div>
        </div>
      `,
      style: {
        fontSize: '14px',
        width: 400,
        whiteSpace: 'nowrap'
      },
      useHTML: true
    },
    xAxis: {
      accessibility: {
        description: '',
        enabled: true
      },
      endOnTick: false,
      labels: {
        enabled: false
      },
      lineWidth: 0,
      startOnTick: false,
      tickLength: 0
    },
    yAxis: {
      accessibility: {
        description: '',
        enabled: true
      },
      endOnTick: false,
      gridLineWidth: 0,
      labels: {
        enabled: false
      },
      lineWidth: 0,
      maxPadding: 0.001,
      minPadding: 0.001,
      startOnTick: false,
      tickLength: 0,
      title: {
        enabled: false
      }
    }
  }
}

const generateSeriesFromDataset = currentTheme => {
  return [
    {
      data: courseDeciles ? [
        [
          getCourseDecile(0),
          getCourseDecile(3),
          getCourseDecile(5),
          getCourseDecile(7),
          getCourseDecile(10)
        ]
      ] : []
    },
    {
      data: props.dataset.student ? [[0, props.dataset.student.raw]] : [],
      marker: {
        fillColor: currentTheme.colors.primary,
        lineWidth: 0,
        radius: 4,
        states: {
          hover: {
            enabled: false
          }
        }
      },
      type: 'scatter'
    }
  ]
}

const getCourseDecile = index => {
  return size(courseDeciles) > index ? courseDeciles[index] : null
}
</script>

<style>
.boxplot-tooltip-font-family {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.boxplot-tooltip-header {
  background-color: rgb(var(--v-theme-surface-light));
  border-bottom: 1px solid rgb(var(--v-theme-surface-light));;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-size: 16px;
  font-weight: 500;
}
</style>
