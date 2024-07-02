<template>
  <div id="student-terms-container" class="m-3 p-0">
    <div class="align-center d-flex mb-2 px-2">
      <div class="pt-1">
        <h2 class="student-section-header mr-2">Classes</h2>
      </div>
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
      <div v-if="currentUser.canReadDegreeProgress" class="flex-shrink-1">
        <router-link
          id="view-degree-checks-link"
          target="_blank"
          :to="getDegreeCheckPath()"
        >
          Degree Checks<span class="sr-only"> of {{ student.name }} (will open new browser tab)</span>
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
        class="bg-grey-lighten-5 w-100"
        @click="year.isOpen = !year.isOpen"
      >
        <v-container :class="year.isOpen ? 'border-e-thin border-s-thin border-t-thin' : 'border-thin'" fluid>
          <v-row align="center">
            <v-col class="align-center d-flex px-0 text-left" :class="{'pb-0': year.isOpen}">
              <v-icon
                class="mx-2"
                color="primary"
                :icon="year.isOpen ? mdiMenuDown : mdiMenuRight"
                size="large"
              />
              <h3 class="font-size-18 text-primary">{{ `Fall ${year.label - 1} - Summer ${year.label}` }}</h3>
            </v-col>
            <v-col class="font-weight-500 text-grey-darken-3" cols="1">
              {{ sumBy(year.terms, 'enrolledUnits') || 0 }} Units
            </v-col>
          </v-row>
        </v-container>
      </button>
      <transition name="drawer">
        <div
          v-show="year.isOpen"
          :aria-expanded="year.isOpen"
          class="border-b-thin border-e-thin border-s-thin drawer"
        >
          <v-container class="pa-0" fluid>
            <v-row no-gutters>
              <v-col cols="4">
                <StudentEnrollmentTerm
                  :id="`term-fall-${year.label - 1}`"
                  class="bg-grey-lighten-5"
                  :student="student"
                  :term="getTerm(`Fall ${year.label - 1}`, year)"
                />
              </v-col>
              <v-col cols="4">
                <StudentEnrollmentTerm
                  :id="`term-spring-${year.label}`"
                  class="bg-grey-lighten-5"
                  :student="student"
                  :term="getTerm(`Spring ${year.label}`, year)"
                />
              </v-col>
              <v-col cols="4">
                <StudentEnrollmentTerm
                  :id="`term-summer-${year.label}`"
                  class="bg-grey-lighten-5"
                  :student="student"
                  :term="getTerm(`Summer ${year.label}`, year)"
                />
              </v-col>
            </v-row>
          </v-container>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import StudentEnrollmentTerm from '@/components/student/profile/StudentEnrollmentTerm'
import {alertScreenReader, studentRoutePath} from '@/lib/utils'
import {each, find, groupBy, includes, map, orderBy, sumBy} from 'lodash'
import {mdiArrowDownThin, mdiArrowUpThin, mdiMenuDown, mdiMenuRight} from '@mdi/js'
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
    year.isOpen = expanded
  })
  alertScreenReader(`All of the academic years have been ${expanded.value ? 'collapsed' : 'expanded'}`)
}

const getDegreeCheckPath = () => {
  const currentDegreeCheck = find(props.student.degreeChecks, 'isCurrent')
  if (currentDegreeCheck) {
    return `/student/degree/${currentDegreeCheck.id}`
  } else if (currentUser.canEditDegreeProgress) {
    return `${studentRoutePath(props.student.uid, currentUser.inDemoMode)}/degree/create`
  } else {
    return `${studentRoutePath(props.student.uid, currentUser.inDemoMode)}/degree/history`
  }
}

const getTerm = (termName, year) => find(year.terms, {'termName': termName}) || {termId: sisIdForTermName(termName), termName}

const sort = () => enrollmentTermsByYear.value = orderBy(enrollmentTermsByYear.value, 'label', yearSortOrder.value)

const toggleSortOrder = () => {
  yearSortOrder.value = yearSortOrder.value === 'asc' ? 'desc' : 'asc'
  sort()
  alertScreenReader(`The sort order of the academic years has changed to ${yearSortOrder.value}ending`)
}
</script>

<style scoped>
.drawer {
  background-color: #f5fbff;
}
</style>

<style scoped>
.color-black {
  color: #000;
}
</style>
