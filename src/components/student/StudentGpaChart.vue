<template>
  <div class="d-flex">
    <highcharts
      v-if="options"
      :id="`student-chart-gpa-container-${student.uid}`"
      ref="highchartsRef"
      v-highchartsA11y
      :options="options"
    />
    <v-btn
      v-if="isChartLoaded"
      :id="`student-chart-gpa-sonify-btn-${student.uid}`"
      :aria-label="`Play chart audio, ${chartDescription}`"
      class="text-primary d-flex"
      density="compact"
      :icon="isPlayingSound ? mdiStopCircle : mdiPlayCircle"
      size="22"
      title="Play chart audio"
      variant="text"
      @click="onClickPlay"
    />
  </div>
</template>

<script setup>
import {eachRight, first, get, last, round, size} from 'lodash'
import {mdiPlayCircle, mdiStopCircle} from '@mdi/js'
import {nextTick, onMounted, ref} from 'vue'
import {useTheme} from 'vuetify'
import {numFormat} from '@/lib/utils'

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

const highchartsRef = ref()
const isChartLoaded = ref(false)
const isPlayingSound = ref(false)
const options = ref(undefined)

onMounted(() => {
  const currentTheme = useTheme().current.value
  const maximumTerm = get(first(props.student.termGpa), 'termName') || get(first(props.student.termGpa), 'name')
  const minimumTerm = get(last(props.student.termGpa), 'termName') || get(last(props.student.termGpa), 'name')
  options.value = {
    accessibility: {
      enabled: true,
      keyboardNavigation: {
        enabled: true,
        seriesNavigation: {
          mode: 'serialize'
        }
      },
      landmarkVerbosity: 'disabled',
      point: {
        valueDecimals: 3,
        valueDescriptionFormat: '{xDescription}: {value} GPA'
      },
      screenReaderSection: {
        beforeChartFormat: '<div>{chartTitle}</div><div>{typeDescription}</div><div>{chartSubtitle}</div><div>{chartLongdesc}</div><div>{viewTableButton}</div><div>{xAxisDescription}</div><div>{yAxisDescription}</div><div>{annotationsTitle}{annotationsList}</div>'
      }
    },
    chart: {
      height: 50,
      type: 'area',
      width: props.width
    },
    colors: [currentTheme.colors.primary],
    credits: {
      enabled: false
    },
    legend: {
      enabled: false
    },
    plotOptions: {
      line: {
        accessibility: {
          description: '',
          enabled: true,
          keyboardNavigation: {
            enabled: true
          }
        }
      }
    },
    series: [
      {
        accessibility: {
          enabled: true,
          keyboardNavigation: {
            enabled: true
          }
        },
        clip: false,
        data: generateGpaDataSeries(currentTheme),
        events: {
          afterAnimate: () => nextTick(() => isChartLoaded.value = true)
        },
        marker: {
          enabled: true
        },
        states: {
          hover: {
            enabled: true
          }
        },
        type: 'line'
      }
    ],
    sonification: {
      defaultInstrumentOptions: {
        mapping: {
          pitch: function(e) {
            // Return a note number where 0 is c0.
            // We add 2 octaves, making the lowest note c2 (0.0 GPA).
            return (10 * round(e.point.y, 1)) + 24
          }
        }
      },
      duration: 2000,
      events: {
        onPlay: () => isPlayingSound.value = true,
        onStop: () => isPlayingSound.value = false
      }
    },
    title: {
      style: {display: 'none'},
      text: props.chartDescription,
      useHTML: true
    },
    tooltip: {
      borderRadius: 8,
      distance: 50,
      enabled: true,
      format: '{description}',
      outside: true,
      valueDecimals: 3
    },
    yAxis: {
      accessibility: {
        description: 'GPA',
        enabled: true,
        rangeDescription: 'Range: 0 to 5'
      },
      endOnTick: false,
      labels: {
        enabled: false
      },
      plotLines: [
        {
          color: currentTheme.colors['surface-variant'],
          dashStyle: 'dot',
          width: 1,
          value: 2
        }
      ],
      softMin: 1.9,
      startOnTick: false,
      tickPositions: [],
      title: {
        text: null
      }
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
    }
  }
})

const generateGpaDataSeries = (currentTheme) => {
  const series = []
  let i = 0
  eachRight(props.student.termGpa, term => {
    series.push({
      accessibility: {
        enabled: true
      },
      description: `${term.termName || term.name} GPA is <b>${numFormat(term.gpa, '0.000')}</b>`,
      marker: {
        enabled: true,
        fillColor: 'transparent',
        lineColor: 'transparent',
        radius: 1
      },
      name: `${term.termName || term.name}`,
      x: i,
      y: term.gpa
    })
    i++
  })
  if (size(series)) {
    const lastElement = last(series)
    const fillColor = lastElement.y < 2 ? currentTheme.colors.error : currentTheme.colors.primary
    lastElement.marker = {
      enabled: true,
      fillColor: fillColor,
      radius: 5
    }
  }
  return series
}

const onClickPlay = () => {
  const {chart} = highchartsRef.value
  chart.toggleSonify()
}
</script>
