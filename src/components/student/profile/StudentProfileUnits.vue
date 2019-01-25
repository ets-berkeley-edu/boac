<template>
  <div class="d-flex flex-row">
    <div id="student-units-completed"
         class="text-center w-50">
      <div class="data-number" v-if="cumulativeUnits">{{cumulativeUnits}}</div>
      <div class="data-number" v-if="!cumulativeUnits">--<span class="sr-only">No data</span></div>
      <div class="text-uppercase">Units Completed</div>
    </div>
    <div id="student-unit-totals" class="border-left text-left">
      <div class="text-uppercase">Unit Totals</div>
      <StudentUnitsChart :currentEnrolledUnits="currentEnrolledUnits"
                         :cumulativeUnits="cumulativeUnits"
                         v-if="cumulativeUnits || currentEnrolledUnits"/>
      <div class="section-label"
           v-if="!cumulativeUnits && !currentEnrolledUnits">
          Units Not Yet Available
      </div>
      <div id="student-currently-enrolled-units"
           class="sr-only"
           v-if="cumulativeUnits || currentEnrolledUnits">
        Currently enrolled units: {{ currentEnrolledUnits || '0' }}
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
.data-number {
  font-size: 42px;
  line-height: 1.2em;
}
</style>
