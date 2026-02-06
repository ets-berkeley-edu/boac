<template>
  <highcharts
    v-if="options"
    ref="highchartsRef"
    v-highchartsA11y
    class="student-boxplot"
    :options="options"
  />
</template>

<script setup>
import {get} from 'lodash'
import {onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'

const props = defineProps({
  axisDescription: {
    required: true,
    type: String
  },
  chartDescription: {
    required: true,
    type: String
  },
  chartSummary: {
    default: '',
    required: false,
    type: String
  },
  dataset: {
    required: true,
    type: Object
  },
  numericId: {
    required: true,
    type: String
  },
  studentName: {
    required: true,
    type: String
  }
})

const courseDeciles = get(props.dataset, 'courseDeciles')
const highchartsRef = ref()
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
      landmarkVerbosity: 'disabled',
      screenReaderSection: {
        beforeChartFormat: `<div>{typeDescription}</div><div>${props.chartSummary}</div><div>{yAxisDescription}</div>`
      },
      typeDescription: `Boxplot with two data series representing the student's ${props.axisDescription} compared with the overall class.`
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
        color: currentTheme.colors['chart-boxplot'],
        enableMouseTracking: false,
        fillColor: currentTheme.colors['chart-boxplot'],
        lineWidth: 1,
        medianColor: currentTheme.colors['chart-boxplot-median'],
        medianWidth: 3,
        whiskerLength: 9,
        whiskerWidth: 1
      },
      series: {
        accessibility: {
          enabled: true,
          keyboardNavigation: {
            enabled: true
          }
        }
      }
    },
    series: generateSeriesFromDataset(currentTheme),
    title: {
      style: {display: 'none'},
      text: props.chartDescription
    },
    tooltip: {
      backgroundColor: currentTheme.colors.surface,
      borderColor: currentTheme.colors['surface-light'],
      borderRadius: 16,
      headerFormat: `
        <div class="align-center boxplot-tooltip-font-family boxplot-tooltip-header d-flex justify-space-between px-3 py-2">
          <div>Student Score</div>
          <div class="ml-3 pl-5">${get(props.dataset.student, 'raw', '&mdash;')}</div>
        </div>
      `,
      hideDelay: 0,
      outside: true,
      padding: 0,
      pointFormat: `
        <div class="boxplot-tooltip-font-family px-3 py-2 w-100">
          <div class="align-center d-flex justify-space-between">
            <div>Maximum</div>
            <div class="ml-3 pl-5">${get(courseDeciles, 10, '&mdash;')}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>70th Percentile</div>
            <div class="ml-3 pl-5">${get(courseDeciles, 7, '&mdash;')}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>50th Percentile</div>
            <div class="ml-3 pl-5">${get(courseDeciles, 5, '&mdash;')}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>30th Percentile</div>
            <div class="ml-3 pl-5">${get(courseDeciles, 3, '&mdash;')}</div>
          </div>
          <div class="align-center d-flex justify-space-between pt-1">
            <div>Minimum</div>
            <div class="ml-3 pl-5">${get(courseDeciles, 0, '&mdash;')}</div>
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
        description: props.axisDescription,
        enabled: true,
        rangeDescription: 'Range: 0 to 100'
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
      accessibility: {
        description: `5 data points representing ${props.axisDescription} by percentile`,
        keyboardNavigation: {
          enabled: true
        },
        point: {
          descriptionFormat: 'minimum: {low}, 30th percentile: {q1}, 50th percentile: {median}, 70th percentile: {q3}, maximum: {high}'
        }
      },
      data: courseDeciles ? [
        [
          get(courseDeciles, 0, null),
          get(courseDeciles, 3, null),
          get(courseDeciles, 5, null),
          get(courseDeciles, 7, null),
          get(courseDeciles, 10, null)
        ]
      ] : [],
      keys: ['low', 'q1', 'median', 'q3', 'high'],
      name: `Overall class ${props.axisDescription}`,
      type: 'boxplot'
    },
    {
      accessibility: {
        keyboardNavigation: {
          enabled: true
        },
        point: {
          descriptionFormat: '{y}'
        }
      },
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
      name: `${props.studentName} ${props.axisDescription}`,
      type: 'scatter'
    }
  ]
}
</script>

<style>
.boxplot-tooltip-font-family {
  font-family: Verdana, "Open Sans", Roboto, Helvetica, Arial, sans-serif;
}
.boxplot-tooltip-header {
  background-color: rgb(var(--v-theme-surface-light));
  border-bottom: 1px solid rgb(var(--v-theme-surface-light));;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-size: 16px;
  font-weight: 500;
}
.student-boxplot {
  max-width: 90px;
  width: 100% !important;
}
.student-boxplot .highcharts-container, .student-boxplot .highcharts-root {
  max-width: 85px;
  width: 100% !important;
}
</style>
