<template>
  <div v-if="options">
    <highcharts
      id="student-chart-units-container"
      class="student-chart-units-container"
      :options="options"
    />
  </div>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'StudentUnitsChart',
  mixins: [Util],
  props: {
    cumulativeUnits: {
      required: true,
      type: Number
    },
    currentEnrolledUnits: {
      required: true,
      type: Number
    },
    student: {
      required: true,
      type: Object
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
      const description = `${this.student.firstName} ${this.student.lastName} is currently enrolled in ${this.currentEnrolledUnits || 'zero'} units and has completed ${this.cumulativeUnits || '0'} units.`
      const yMax = this._max([120, this.currentEnrolledUnits + this.cumulativeUnits])
      return {
        accessibility: {
          description,
          enabled: true,
          keyboardNavigation: {
            enabled: true
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
            description,
            enabled: true,
            exposeAsGroupOnly: true,
            keyboardNavigation: {
              enabled: true
            }
          },
          column: {
            stacking: 'normal',
            groupPadding: 0,
            pointPadding: 0
          },
          enableMouseTracking: false,
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
            accessibility: {
              description: `${this.currentEnrolledUnits} currently enrolled units`,
              enabled: true
            },
            name: 'Term units',
            data: [this.currentEnrolledUnits]
          },
          {
            accessibility: {
              description: `${this.cumulativeUnits} cumulative units`,
              enabled: true
            },
            name: 'Cumulative units',
            data: [this.cumulativeUnits]
          }
        ],
        title: {
          text: ''
        },
        tooltip: {
          animation: false,
          backgroundColor: '#fff',
          borderColor: '#eee',
          borderRadius: 8,
          distance: 16,
          headerFormat: '',
          hideDelay: 0,
          outside: false,
          pointFormat: `
            <div class="units-chart-font-family w-100">
              <div class="align-center d-flex">
                <div><div style="background-color: #aec9eb; height: 12px; width: 12px;"></div></div>
                <div class="pl-1 text-left text-no-wrap">Units Completed</div>
                <div class="font-weight-bold pl-2 text-right w-100">${this.cumulativeUnits || '0'}</div>
              </div>
              <div class="align-center d-flex w-100">
                <div><div style="background-color: #d6e4f9; height: 12px; width: 12px;"></div></div>
                <div class="pl-1 text-left text-no-wrap">Currently Enrolled Units</div>
                <div class="font-weight-bold pl-2 text-right w-100">${this.currentEnrolledUnits || '0'}</div>
              </div>
            </div>
          `,
          positioner: (w, h, point) => {
            return {
              x: point.plotX - 35,
              y: point.plotY + 35
            }
          },
          style: {
            fontSize: '14px',
            whiteSpace: 'nowrap',
            width: 600
          },
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
          max: yMax,
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

<style>
.student-chart-units-container,
.student-chart-units-container .highcharts-container,
.student-chart-units-container .highcharts-root {
  overflow: visible !important;
}
.units-chart-font-family {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}
</style>
