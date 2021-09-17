<template>
  <div class="d-flex flex-wrap h-100 py-2">
    <div
      id="cumulative-units"
      class="cumulative-units text-center py-2"
    >
      <div v-if="cumulativeUnits" class="data-number">{{ cumulativeUnits }}</div>
      <div v-if="!cumulativeUnits" class="data-number">--<span class="sr-only">No data</span></div>
      <div class="cumulative-units-label text-uppercase">Units Completed</div>
    </div>
    <div id="units-chart" class="border-left units-chart py-2">
      <div class="ml-4">
        <h4 class="font-weight-bold mb-1 unit-totals-label">Unit Totals</h4>
        <div>
          <StudentUnitsChart
            v-if="cumulativeUnits || currentEnrolledUnits"
            class="student-units-chart"
            :cumulative-units="cumulativeUnits"
            :current-enrolled-units="currentEnrolledUnits || 0"
            :student="student"
          />
          <div
            v-if="!cumulativeUnits && !currentEnrolledUnits"
            class="section-label"
          >
            Units Not Yet Available
          </div>
        </div>
        <div
          v-if="cumulativeUnits || currentEnrolledUnits"
          id="currently-enrolled-units"
          class="sr-only"
        >
          Currently enrolled units: {{ currentEnrolledUnits || '0' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StudentUnitsChart from '@/components/student/StudentUnitsChart'
import Util from '@/mixins/Util'

export default {
  name: 'StudentProfileUnits',
  components: {
    StudentUnitsChart
  },
  mixins: [Context, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    cumulativeUnits: undefined,
    currentEnrolledUnits: undefined
  }),
  created() {
    this.cumulativeUnits = this.$_.get(this.student, 'sisProfile.cumulativeUnits')
    const currentEnrollmentTerm = this.$_.find(
      this.$_.get(this.student, 'enrollmentTerms'),
      {
        termId: this.$_.toString(this.$config.currentEnrollmentTermId)
      }
    )
    if (currentEnrollmentTerm) {
      this.currentEnrolledUnits = this.$_.get(currentEnrollmentTerm, 'enrolledUnits')
    }
  }
}
</script>

<style scoped>
.cumulative-units {
  font-weight: 700;
  min-width: 120px;
  white-space: nowrap;
  width: 40%;
}
.cumulative-units-label {
  color: #999;
  font-size: 11px;
}
.data-number {
  font-size: 28px;
  line-height: 1.4em;
}
.unit-totals-label {
  color: #555;
  font-size: 11px;
  text-transform: uppercase;
}
.units-chart {
  min-width: 225px;
  width: 50%;
}
.student-units-chart {
  min-width: 200px;
  width: 100%;
}
</style>
