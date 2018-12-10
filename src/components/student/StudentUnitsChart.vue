<template>
  <highcharts class="student-chart-units-container"
              id="student-chart-units-container"
              ref="studentUnitsChart"
              :options="unitsChartOptions"
              aria-hidden="true">
  </highcharts>
</template>

<script>
export default {
  name: 'StudentUnitsChart',
  data: () => ({
    unitsChartOptions: {
      chart: {
        backgroundColor: 'transparent',
        height: 60,
        inverted: true,
        spacingLeft: 5,
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
      series: [],
      title: {
        text: ''
      },
      tooltip: {
        borderColor: '#666',
        headerFormat: '',
        hideDelay: 0,
        pointFormat: '',
        positioner: function() {
          return {
            x: -35,
            y: 35
          };
        },
        width: 240,
        shadow: false,
        useHTML: true
      },
      xAxis: {
        labels: {
          enabled: false
        },
        lineWidth: 0,
        startOnTick: false,
        tickLength: 0
      },
      yAxis: {
        min: 0,
        max: 120,
        gridLineColor: '#000000',
        tickInterval: 30,
        labels: {
          align: 'center',
          distance: 0,
          overflow: false,
          style: {
            color: '#999999',
            fontFamily: 'Helvetica, Arial, sans',
            fontSize: '12px',
            fontWeight: 'bold'
          }
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
  }),
  props: {
    cumulativeUnits: Number,
    currentEnrolledUnits: Number
  },
  mounted() {
    this.renderUnitsToChart();
  },
  methods: {
    renderUnitsToChart() {
      this.unitsChartOptions.series = [
        {
          name: 'Term units',
          data: [this.currentEnrolledUnits]
        },
        {
          name: 'Cumulative units',
          data: [this.cumulativeUnits]
        }
      ];
      this.unitsChartOptions.tooltip.pointFormat = this.generateTooltipHtml();
      this.unitsChartOptions.width = this.$refs.studentUnitsChart.$el.parentNode.clientWidth;
    },
    generateTooltipHtml() {
      return `
        <div class="student-chart-units-tooltip-content">
          <div class="student-chart-units-tooltip-row">
            <div class="student-chart-units-tooltip-swatch swatch-blue-medium"></div>
            <div class="student-chart-units-tooltip-label">Units Completed</div>
            <div class="student-chart-units-tooltip-value">${
              this.cumulativeUnits
            }</div>
          </div>
          <div class="student-chart-units-tooltip-row">
            <div class="student-chart-units-tooltip-swatch swatch-blue-light"></div>
            <div class="student-chart-units-tooltip-label">Currently Enrolled Units</div>
            <div class="student-chart-units-tooltip-value">${
              this.currentEnrolledUnits
            }</div>
          </div>
        </div>`;
    }
  }
};
</script>

<style>
.student-chart-units-container .highcharts-container {
  overflow: visible !important;
}
.student-chart-units-container .highcharts-series rect {
  stroke-width: 0;
}
.student-chart-units-container .highcharts-tooltip {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  line-height: 1.4em;
  min-width: 240px;
  padding: 0;
}
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
.student-chart-units-container g.highcharts-tooltip {
  display: none !important;
}
.student-chart-units-container .highcharts-tooltip span {
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
  width: auto !important;
}
.student-chart-units-container .highcharts-container {
  overflow: visible !important;
  z-index: auto !important;
}
.student-chart-units-tooltip-content {
  color: #000;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 14px;
  font-weight: 400;
  margin: 0;
  padding: 8px 15px;
}
.student-chart-units-tooltip-header {
  background: #eee;
  border-bottom: 1px solid #ddd;
  display: flex;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  font-size: 16px;
  font-weight: 400;
  margin-bottom: 0;
  padding: 8px 15px;
  text-align: left;
}
.student-chart-units-tooltip-label {
  flex: 0.8;
}
.student-chart-units-tooltip-row {
  align-items: center;
  display: flex;
  line-height: 1.5em;
}
.student-chart-units-tooltip-swatch {
  height: 13px;
  margin-right: 5px;
  width: 13px;
}
.student-chart-units-tooltip-value {
  flex: 0.2;
  font-weight: bold;
  text-align: right;
}
.swatch-blue-medium {
  background-color: #aec9eb;
}
.swatch-blue-light {
  background-color: #d6e4f9;
}
</style>
