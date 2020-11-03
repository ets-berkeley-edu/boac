<template>
  <highcharts
    v-if="options"
    id="student-chart-units-container"
    ref="studentUnitsChart"
    class="student-chart-container student-chart-units-container"
    :options="options"
  />
</template>

<script>
export default {
  name: 'StudentUnitsChart',
  props: {
    chartDescription: {
      required: true,
      type: String
    },
    cumulativeUnits: {
      required: true,
      type: Number
    },
    currentEnrolledUnits: {
      required: true,
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
          height: 40,
          inverted: true,
          spacingLeft: 5,
          spacingTop: 5,
          spacingBottom: 5,
          type: 'column'
        },
        colors: ['#d6e4f9', '#aec9eb'],
        credits: {
          enabled: false
        },
        legend: {
          enabled: false
        },
        navigation: {
          buttonOptions: {
            enabled: false
          }
        },
        plotOptions: {
          accessibility: {
            description: this.chartDescription,
            enabled: true,
            exposeAsGroupOnly: true,
            keyboardNavigation: {
              enabled: true
            },
            pointDescriptionFormatter: point => `${point.index + 1}. ${point.name} (y value: ${point.y})`
          },
          column: {
            stacking: 'normal',
            groupPadding: 0,
            pointPadding: 0
          },
          series: {
            states: {
              hover: {
                enabled: false
              }
            }
          }
        },
        series: [
          {
            name: 'Term units',
            data: [this.currentEnrolledUnits]
          },
          {
            name: 'Cumulative units',
            data: [this.cumulativeUnits]
          }
        ],
        title: {
          text: ''
        },
        tooltip: {
          borderColor: '#666',
          headerFormat: '',
          hideDelay: 0,
          pointFormat: `
            <div class="student-chart-tooltip-content">
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-swatch swatch-blue-medium"></div>
                <div class="student-chart-tooltip-label">Units Completed</div>
                <div class="student-chart-tooltip-value">${this.cumulativeUnits || '0'}</div>
              </div>
              <div class="student-chart-tooltip-row">
                <div class="student-chart-tooltip-swatch swatch-blue-light"></div>
                <div class="student-chart-tooltip-label">Currently Enrolled Units</div>
                <div class="student-chart-tooltip-value">${this.currentEnrolledUnits || '0'}</div>
              </div>
            </div>
          `,
          positioner: () => {
            return {
              x: -35,
              y: 35
            }
          },
          width: 240,
          shadow: false,
          useHTML: true
        },
        xAxis: {
          accessibility: {
            description: 'Time',
            enabled: true
          },
          labels: {
            enabled: false
          },
          lineWidth: 0,
          startOnTick: false,
          tickLength: 0
        },
        yAxis: {
          accessibility: {
            description: 'Units',
            enabled: true
          },
          min: 0,
          max: 120,
          gridLineColor: '#000000',
          tickInterval: 30,
          labels: {
            align: 'center',
            overflow: true,
            padding: 0,
            style: {
              color: '#999999',
              fontFamily: 'Helvetica, Arial, sans',
              fontSize: '11px',
              fontWeight: 'bold'
            },
            y: 12
          },
          stackLabels: {
            enabled: false
          },
          title: {
            enabled: false
          },
          gridZIndex: 1000
        }
      }
    }
  }
}
</script>

<style src="./student-chart.css">
</style>

<style>
.student-chart-units-container .highcharts-tooltip::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 0 1px 1px;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  top: -6px;
  left: 40px;
  transform: rotate(135deg);
  width: 10px;
}
.student-chart-units-container .swatch-blue-medium {
  background-color: #aec9eb;
}
.student-chart-units-container .swatch-blue-light {
  background-color: #d6e4f9;
}
</style>
