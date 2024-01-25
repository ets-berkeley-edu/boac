<template>
  <div class="d-flex flex-wrap h-100 py-2">
    <div
      id="cumulative-units"
      class="cumulative-units text-center units py-2"
    >
      <div v-if="cumulativeUnits" class="data-number">{{ cumulativeUnits }}</div>
      <div v-if="!cumulativeUnits" class="data-number">--<span class="sr-only">No data</span></div>
      <div class="cumulative-units-label text-uppercase">Units Completed</div>
    </div>
    <div v-if="!isGraduate(student)" id="units-chart" class="border-left units-chart py-2">
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
    <div v-if="isGraduate(student)" class="units currently-enrolled-units text-center border-left py-2">
      <div id="units-currently-enrolled" class="data-number">{{ currentEnrolledUnits || '0' }}</div>
      <div class="cumulative-units-label text-uppercase">Currently Enrolled Units</div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import StudentUnitsChart from '@/components/student/StudentUnitsChart'
import Util from '@/mixins/Util'
import {isGraduate} from '@/berkeley'

export default {
  name: 'StudentProfileUnits',
  mixins: [Context, Util],
  components: {StudentUnitsChart},
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
    this.cumulativeUnits = this._get(this.student, 'sisProfile.cumulativeUnits')
    const currentEnrollmentTerm = this._find(
      this._get(this.student, 'enrollmentTerms'),
      {
        termId: this._toString(this.config.currentEnrollmentTermId)
      }
    )
    if (currentEnrollmentTerm) {
      this.currentEnrolledUnits = this._get(currentEnrollmentTerm, 'enrolledUnits')
    }
  },
  methods: {
    isGraduate
  }
}
</script>

<style scoped>
.cumulative-units {
  width: 40%;
}
.cumulative-units-label {
  color: #999;
  font-size: 11px;
}
.currently-enrolled-units {
  width: 60%;
}
.data-number {
  font-size: 28px;
  line-height: 1.4em;
}
.student-units-chart {
  min-width: 200px;
  width: 100%;
}
.unit-totals-label {
  color: #555;
  font-size: 11px;
  text-transform: uppercase;
}
.units {
  font-weight: 700;
  min-width: 120px;
  white-space: nowrap;
}
.units-chart {
  min-width: 225px;
  width: 50%;
}
</style>
