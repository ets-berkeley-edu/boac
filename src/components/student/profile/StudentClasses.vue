<template>
  <div id="student-terms-container" aria-labelledby="student-classes-header" role="region">
    <div class="align-center d-flex">
      <h2 id="student-classes-header" class="student-section-header">Classes</h2>
      <div>
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="toggle-collapse-all-years"
          variant="text"
          @click="expandCollapseAll"
        >
          <v-icon :icon="expanded ? mdiMenuDown : mdiMenuRight" />
          {{ expanded ? 'Collapse' : 'Expand' }} all years
        </v-btn>
      </div>
      <div v-if="enrollmentTermsByYear.length > 1">|</div>
      <div class="flex-grow-1">
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="sort-academic-year"
          variant="text"
          @click="toggleSortOrder"
        >
          Sort academic year
          <v-icon :icon="yearSortOrder === 'desc' ? mdiArrowDownThin : mdiArrowUpThin" />
        </v-btn>
      </div>
      <div v-if="currentUser.canReadDegreeProgress">
        <router-link
          id="view-degree-checks-link"
          target="_blank"
          :to="getDegreeCheckPath(student)"
        >
          <div class="align-center d-flex text-anchor">
            <div>
              Undergraduate Degree Checks <span class="sr-only">of {{ student.name }} (will open new browser tab)</span>
            </div>
            <v-icon class="ml-1" :icon="mdiOpenInNew" size="18" />
          </div>
        </router-link>
      </div>
    </div>
    <div
      v-for="year in enrollmentTermsByYear"
      :id="`academic-year-${year.label}-container`"
      :key="year.label"
      class="pt-3 w-100"
    >
      <button
        :id="`academic-year-${year.label}-toggle`"
        class="w-100"
        @click="year.isOpen = !year.isOpen"
      >
        <v-container
          :class="year.isOpen ? 'border-e-thin border-s-thin border-t-thin' : 'border-thin'"
          fluid
        >
          <v-row>
            <v-col
              class="align-center d-flex pt-2 px-0 text-left"
              :class="{
                'pb-0': !$vuetify.display.smAndUp,
                'pb-2': $vuetify.display.smAndUp
              }"
              :cols="$vuetify.display.smAndUp ? 10 : 12"
            >
              <v-icon
                class="mx-1"
                color="primary"
                :icon="year.isOpen ? mdiMenuDown : mdiMenuRight"
                size="large"
              />
              <h3 class="font-size-18 text-primary">{{ `Fall ${year.label - 1} - Summer ${year.label}` }}</h3>
            </v-col>
            <v-col
              class="font-weight-500 pt-2 text-right text-surface-variant text-no-wrap"
              :class="{
                'pb-0': year.isOpen,
                'pb-2': !year.isOpen
              }"
              :cols="$vuetify.display.smAndUp ? 2 : 12"
            >
              {{ sumBy(year.terms, 'enrolledUnits') || 0 }} Units
            </v-col>
          </v-row>
        </v-container>
      </button>
      <v-expand-transition>
        <div
          v-if="year.isOpen"
          :aria-expanded="year.isOpen"
          class="border-b-thin border-e-thin border-s-thin"
        >
          <v-container class="pl-6 pt-0" fluid>
            <v-row>
              <v-col :cols="$vuetify.display.lgAndUp ? 4 : 12">
                <StudentEnrollmentTerm
                  :id="`term-fall-${year.label - 1}`"
                  :column-index="0"
                  :student="student"
                  :term="getTerm(`Fall ${year.label - 1}`, year)"
                />
              </v-col>
              <v-col :cols="$vuetify.display.lgAndUp ? 4 : 12">
                <StudentEnrollmentTerm
                  :id="`term-spring-${year.label}`"
                  :column-index="1"
                  :student="student"
                  :term="getTerm(`Spring ${year.label}`, year)"
                />
              </v-col>
              <v-col :cols="$vuetify.display.lgAndUp ? 4 : 12">
                <StudentEnrollmentTerm
                  :id="`term-summer-${year.label}`"
                  :column-index="2"
                  :student="student"
                  :term="getTerm(`Summer ${year.label}`, year)"
                />
              </v-col>
            </v-row>
          </v-container>
        </div>
      </v-expand-transition>
    </div>
  </div>
</template>

<script setup>
import StudentEnrollmentTerm from '@/components/student/profile/StudentEnrollmentTerm'
import {alertScreenReader, getDegreeCheckPath} from '@/lib/utils'
import {each, find, groupBy, includes, map, orderBy, sumBy} from 'lodash'
import {mdiArrowDownThin, mdiArrowUpThin, mdiMenuDown, mdiMenuRight, mdiOpenInNew} from '@mdi/js'
import {onMounted, ref} from 'vue'
import {sisIdForTermName} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const config = contextStore.config
const currentUser = contextStore.currentUser
const enrollmentTermsByYear = ref({})
const expanded = ref(false)
const yearSortOrder = ref('desc')

onMounted(() => {
  const grouped = groupBy(props.student.enrollmentTerms, 'academicYear')
  const enrollmentTerms = map(grouped, (terms, year) => {
    const semesters = [`Fall ${year - 1}`, `Spring ${year}`, `Summer ${year}`]
    return {
      isOpen: includes(semesters, config.currentEnrollmentTerm),
      label: year,
      terms
    }
  })
  sort()
  enrollmentTermsByYear.value = orderBy(enrollmentTerms, 'label', yearSortOrder.value)
})

const expandCollapseAll = () => {
  expanded.value = !expanded.value
  each(enrollmentTermsByYear.value, year => {
    year.isOpen = expanded.value
  })
  alertScreenReader(`All of the academic years have been ${expanded.value ? 'collapsed' : 'expanded'}`)
}

const getTerm = (termName, year) => find(year.terms, {'termName': termName}) || {termId: sisIdForTermName(termName), termName}

const sort = () => enrollmentTermsByYear.value = orderBy(enrollmentTermsByYear.value, 'label', yearSortOrder.value)

const toggleSortOrder = () => {
  yearSortOrder.value = yearSortOrder.value === 'asc' ? 'desc' : 'asc'
  sort()
  alertScreenReader(`The sort order of the academic years has changed to ${yearSortOrder.value}ending`)
}
</script>
