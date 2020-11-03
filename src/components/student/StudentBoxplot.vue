<template>
  <highcharts
    v-if="options"
    :id="`student-chart-boxplot-container-${numericId}`"
    class="student-chart-container student-chart-boxplot-container"
    :options="options"
  />
</template>

<script>
export default {
  name: 'StudentBoxplot',
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
    options: undefined,
    courseDeciles: undefined
  }),
  mounted() {
    this.courseDeciles = this.$_.get(this.dataset, 'courseDeciles')
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
          enabled:true,
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
              pointDescriptionFormatter: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
            },
            color: '#ccc',
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
          borderColor: '#666',
          headerFormat: `
            <div class="student-chart-tooltip-header">
              <div class="student-chart-tooltip-label">User Score</div>
              <div class="student-chart-tooltip-value">${this.$_.get(this.dataset.student, 'raw') || '--'}</div>
            </div>
          `,
          hideDelay: 0,
          pointFormat: `
            <div class="student-chart-tooltip-content visible">
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-label">Maximum</div>
                <div class="student-chart-tooltip-value">${this.getCourseDecile(10) || '--'}</div>
              </div>
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-label">70th Percentile</div>
                <div class="student-chart-tooltip-value">${this.getCourseDecile(7) || '--'}</div>
              </div>
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-label">50th Percentile</div>
                <div class="student-chart-tooltip-value">${this.getCourseDecile(5) || '--'}</div>
              </div>
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-label">30th Percentile</div>
                <div class="student-chart-tooltip-value">${this.getCourseDecile(3) || '--'}</div>
              </div>
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-label">Minimum</div>
                <div class="student-chart-tooltip-value">${this.getCourseDecile(0) || '--'}</div>
              </div>
            </div>
          `,
          positioner: () => {
            return {
              x: 90,
              y: -75
            }
          },
          shadow: false,
          useHTML: true,
          width: 400
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

<style src="./student-chart.css">
</style>

<style>
.student-chart-boxplot-container {
  height: 18px;
  width: 75px;
}
.student-chart-boxplot-container .highcharts-tooltip {
  z-index: 1;
}
.student-chart-boxplot-container .highcharts-tooltip::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 1px 1px 0;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  top: 75px;
  left: -6px;
  transform: rotate(135deg);
  width: 10px;
}
</style>
