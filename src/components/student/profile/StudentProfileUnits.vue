<template>
  <div class="d-flex align-items-center h-100 p-2">
    <div id="cumulative-units"
         class="cumulative-units text-center">
      <div class="data-number" v-if="cumulativeUnits">{{cumulativeUnits}}</div>
      <div class="data-number" v-if="!cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div class="cumulative-units-label text-uppercase">Units Completed</div>
    </div>
    <div id="units-chart" class="units-chart border-left">
      <div class="ml-3">
        <div class="unit-totals-label font-weight-bold">Unit Totals</div>
        <StudentUnitsChart :currentEnrolledUnits="currentEnrolledUnits"
                           :cumulativeUnits="cumulativeUnits"
                           v-if="cumulativeUnits || currentEnrolledUnits"/>
        <div class="section-label"
             v-if="!cumulativeUnits && !currentEnrolledUnits">
            Units Not Yet Available
        </div>
        <div id="currently-enrolled-units"
             class="sr-only"
             v-if="cumulativeUnits || currentEnrolledUnits">
          Currently enrolled units: {{ currentEnrolledUnits || '0' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import StudentUnitsChart from '@/components/student/StudentUnitsChart';
import Util from '@/mixins/Util';

export default {
  name: 'StudentProfileUnits',
  mixins: [Context, Util],
  components: {
    StudentUnitsChart
  },
  props: {
    student: Object
  },
  data: () => ({
    cumulativeUnits: undefined,
    currentEnrolledUnits: undefined
  }),
  created() {
    this.cumulativeUnits = this.get(this.student, 'sisProfile.cumulativeUnits');
    const currentEnrollmentTerm = this.find(
      this.get(this.student, 'enrollmentTerms'),
      {
        termId: this.currentEnrollmentTermId.toString()
      }
    );
    if (currentEnrollmentTerm) {
      this.currentEnrolledUnits = this.get(
        currentEnrollmentTerm,
        'enrolledUnits'
      );
    }
  }
};
</script>

<style scoped>
.cumulative-units {
  font-weight: 700;
  margin-left: 20px;
  white-space: nowrap;
  width: 40%;
}
.cumulative-units-label {
  color: #999;
  font-size: 12px;
}
.data-number {
  font-size: 42px;
  line-height: 1.2em;
}
.units-chart {
  height: 100%;
}
.unit-totals-label {
  color: #555;
  font-size: 14px;
  text-transform: uppercase;
}
</style>
