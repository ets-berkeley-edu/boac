<template>
  <highcharts
    id="student-chart-units-container"
    ref="studentUnitsChart"
    :options="unitsChartOptions"
    class="student-chart-container student-chart-units-container"
    aria-hidden="true">
  </highcharts>
</template>

<script>
export default {
  name: 'StudentUnitsChart',
  props: {
    cumulativeUnits: Number,
    currentEnrolledUnits: Number
  },
  data: () => ({
    unitsChartOptions: {
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
  }),
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
        <div class="student-chart-tooltip-content">
          <div class="student-chart-tooltip-row">
            <div class="student-chart-tooltip-swatch swatch-blue-medium"></div>
            <div class="student-chart-tooltip-label">Units Completed</div>
            <div class="student-chart-tooltip-value">${
        this.cumulativeUnits || '0'
      }</div>
          </div>
          <div class="student-chart-tooltip-row">
            <div class="student-chart-tooltip-swatch swatch-blue-light"></div>
            <div class="student-chart-tooltip-label">Currently Enrolled Units</div>
            <div class="student-chart-tooltip-value">${this
      .currentEnrolledUnits || '0'}</div>
          </div>
        </div>`;
    }
  }
};
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
