<template>
  <v-container class="d-flex h-100" fluid>
    <v-row align="stretch" class="v-row-override-margins">
      <v-col
        id="cumulative-units"
        align-self="center"
        class="cumulative-units text-center units"
      >
        <div>
          <div v-if="cumulativeUnits" class="data-number">{{ cumulativeUnits }}</div>
          <div v-if="!cumulativeUnits" class="data-number">--<span class="sr-only">No data</span></div>
          <div class="cumulative-units-label text-medium-emphasis text-uppercase">Units Completed</div>
        </div>
      </v-col>
      <v-col
        v-if="!isGraduate(student)"
        id="units-chart"
        align-self="center"
        class="border-s-sm d-flex align-center justify-center units-chart"
      >
        <div class="d-flex flex-column pl-4">
          <h4 class="units-label font-weight-bold mb-1 text-medium-emphasis text-uppercase">Unit Totals</h4>
          <StudentUnitsChart
            v-if="cumulativeUnits || currentEnrolledUnits"
            class="flex-grow-0 student-units-chart"
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
      </v-col>
      <v-col
        v-if="isGraduate(student)"
        class="units text-center border-s-sm"
      >
        <div id="units-currently-enrolled" class="data-number">{{ currentEnrolledUnits || '0' }}</div>
        <div class="cumulative-units-label text-medium-emphasis text-uppercase">Currently Enrolled Units</div>
      </v-col>
    </v-row>
  </v-container>
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
  min-width: 150px;
}
.cumulative-units-label {
  font-size: 12px;
}
.data-number {
  font-size: 28px;
  line-height: 1.4em;
}
.student-units-chart {
  min-width: 200px;
}
.units {
  font-weight: 700;
  white-space: nowrap;
}
.units-chart {
  height: 130px;
  min-width: 225px;
}
.units-label {
  font-size: 12px;
}
.v-row-override-margins {
  margin-left: -15px;
}
</style>
