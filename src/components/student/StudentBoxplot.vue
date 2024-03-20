<template>
  <div v-if="options">
    <highcharts :id="`student-chart-boxplot-container-${numericId}`" :options="options" />
  </div>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'StudentBoxplot',
  mixins: [Util],
  props: {
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
  },
  data: () => ({
    courseDeciles: undefined,
    options: undefined
  }),
  mounted() {
    this.courseDeciles = this._get(this.dataset, 'courseDeciles')
    this.options = this.getOptions()
  },
  methods: {
    generateSeriesFromDataset() {
      return [
        {
          data: this.courseDeciles ? [
            [
              this.getCourseDecile(0),
              this.getCourseDecile(3),
              this.getCourseDecile(5),
              this.getCourseDecile(7),
              this.getCourseDecile(10)
            ]
          ] : []
        },
        {
          data: this.dataset.student ? [[0, this.dataset.student.raw]] : [],
          marker: {
            fillColor: '#4a90e2',
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
    },
    getCourseDecile(index) {
      return this.courseDeciles && this.courseDeciles.length > index ? this.courseDeciles[index] : null
    },
    getOptions() {
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
              description: this.chartDescription,
              enabled: true,
              exposeAsGroupOnly: true,
              keyboardNavigation: {
                enabled: true
              },
              valueDescriptionFormat: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
            },
            color: '#ccc',
            enableMouseTracking: false,
            fillColor: '#ccc',
            lineWidth: 1,
            medianColor: '#666',
            medianWidth: 3,
            whiskerLength: 9,
            whiskerWidth: 1
          }
        },
        series: this.generateSeriesFromDataset(),
        title: {
          text: ''
        },
        tooltip: {
          backgroundColor: '#fff',
          borderColor: '#eee',
          borderRadius: 16,
          headerFormat: `
            <div class="align-center boxplot-tooltip-font-family boxplot-tooltip-header d-flex justify-content-between px-3 py-2">
              <div>User Score</div>
              <div class="ml-3 pl-5">${this._get(this.dataset.student, 'raw') || '&mdash;'}</div>
            </div>
          `,
          hideDelay: 0,
          outside: true,
          padding: 0,
          pointFormat: `
            <div class="boxplot-tooltip-font-family px-3 py-2 w-100">
              <div class="align-center d-flex justify-content-between">
                <div>Maximum</div>
                <div class="ml-3 pl-5">${this.getCourseDecile(10) || '&mdash;'}</div>
              </div>
              <div class="align-center d-flex justify-content-between pt-1">
                <div>70th Percentile</div>
                <div class="ml-3 pl-5">${this.getCourseDecile(7) || '&mdash;'}</div>
              </div>
              <div class="align-center d-flex justify-content-between pt-1">
                <div>50th Percentile</div>
                <div class="ml-3 pl-5">${this.getCourseDecile(5) || '&mdash;'}</div>
              </div>
              <div class="align-center d-flex justify-content-between pt-1">
                <div>30th Percentile</div>
                <div class="ml-3 pl-5">${this.getCourseDecile(3) || '&mdash;'}</div>
              </div>
              <div class="align-center d-flex justify-content-between pt-1">
                <div>Minimum</div>
                <div class="ml-3 pl-5">${this.getCourseDecile(0) || '&mdash;'}</div>
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
  }
}
</script>

<style>
.boxplot-tooltip-font-family {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
.boxplot-tooltip-header {
  background-color: #eee;
  border-bottom: 1px solid #eee;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
  font-size: 16px;
  font-weight: 500;
}
</style>
