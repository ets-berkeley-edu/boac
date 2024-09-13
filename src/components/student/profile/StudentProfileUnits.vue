<template>
  <div class="align-center d-flex flex-wrap h-100 py-2">
    <div
      id="cumulative-units"
      class="cumulative-units text-center units py-2"
    >
      <div v-if="cumulativeUnits" class="data-number">{{ cumulativeUnits }}</div>
      <div v-if="!cumulativeUnits" class="data-number">--<span class="sr-only">No data</span></div>
      <div class="cumulative-units-label text-medium-emphasis text-uppercase">Units Completed</div>
    </div>
    <div v-if="!isGraduate(student)" id="units-chart" class="border-s-sm units-chart py-2">
      <div class="ml-4">
        <h4 class="font-weight-bold mb-1 text-medium-emphasis">Unit Totals</h4>
        <StudentUnitsChart
          v-if="cumulativeUnits || currentEnrolledUnits"
          class="student-units-chart"
          :cumulative-units="cumulativeUnits"
          :current-enrolled-units="currentEnrolledUnits || 0"
          :student="student"
        />
        <div v-if="!cumulativeUnits && !currentEnrolledUnits" class="section-label">
          Units Not Yet Available
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
    <div v-if="isGraduate(student)" class="units currently-enrolled-units text-center border-s-sm py-2">
      <div id="units-currently-enrolled" class="data-number">{{ currentEnrolledUnits || '0' }}</div>
      <div class="cumulative-units-label text-medium-emphasis text-uppercase">Currently Enrolled Units</div>
    </div>
  </div>
</template>

<script setup>
import StudentUnitsChart from '@/components/student/StudentUnitsChart'
import {find, get, toString} from 'lodash'
import {isGraduate} from '@/berkeley'
import {onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const cumulativeUnits = ref(undefined)
const currentEnrolledUnits = ref(undefined)

onMounted(() => {
  cumulativeUnits.value = get(props.student, 'sisProfile.cumulativeUnits')
  const currentEnrollmentTerm = find(
    get(props.student, 'enrollmentTerms'),
    {termId: toString(contextStore.config.currentEnrollmentTermId)}
  )
  if (currentEnrollmentTerm) {
    currentEnrolledUnits.value = get(currentEnrollmentTerm, 'enrolledUnits')
  }
})
</script>

<style scoped>
.cumulative-units {
  width: 40%;
}
.cumulative-units-label {
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
.text-medium-emphasis {
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
