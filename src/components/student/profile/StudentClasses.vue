<template>
  <div id="student-terms-container">
    <div class="align-center d-flex flex-wrap">
      <div class="pb-1">
        <h2 class="student-section-header text-primary">Classes</h2>
      </div>
      <div>
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="toggle-collapse-all-years"
          class="pr-2"
          density="compact"
          variant="plain"
          @click="toggle"
        >
          <v-icon v-if="panelsExpanded.length" :icon="mdiMenuDown" />
          <v-icon v-if="!panelsExpanded.length" :icon="mdiMenuRight" />
          {{ panelsExpanded.length ? 'Collapse' : 'Expand' }} all years
        </v-btn>
      </div>
      <div v-if="enrollmentTermsByYear.length > 1">|</div>
      <div>
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="sort-academic-year"
          class="pl-2"
          density="compact"
          variant="plain"
          @click="setOrder"
        >
          <v-icon :icon="currentOrder === 'desc' ? mdiArrowDownThin : mdiArrowUpThin" />
          Sort academic year
        </v-btn>
      </div>
    </div>
    <v-expansion-panels v-model="panelsExpanded" flat multiple>
      <v-expansion-panel
        v-for="year in enrollmentTermsByYear"
        :id="`academic-year-${year.label}-container`"
        :key="year.label"
        class="mt-0 pa-0 student-classes-expansion-panel"
        hide-actions
        :value="year.label"
      >
        <v-expansion-panel-title>
          <template #default="{expanded}">
            <v-icon
              class="expansion-panel-icon"
              color="primary"
              :icon="expanded ? mdiMenuDown : mdiMenuRight"
              size="24"
            />
            <div class="align-center d-flex justify-space-between w-100">
              <div>
                <h3 class="text-primary page-section-header-sub ma-0">{{ `Fall ${year.label - 1} - Summer ${year.label}` }}</h3>
              </div>
              <div class="font-weight-500 text-grey-darken-1">{{ totalUnits(year) || 0 }} Units</div>
            </div>
          </template>
          <template #actions />
        </v-expansion-panel-title>
        <v-expansion-panel-text class="student-classes-expansion-text">
          <div class="align-start d-flex flex-wrap justify-lg-space-evenly w-100">
            <StudentEnrollmentTerm
              v-for="termName in [`Fall ${year.label - 1}`, `Spring ${year.label}`, `Summer ${year.label}`]"
              :id="`term-fall-${year.label - 1}`"
              :key="termName"
              class="student-enrollment-term"
              :student="student"
              :term="getTerm(termName, year)"
            />
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import {mdiArrowDownThin, mdiArrowUpThin, mdiMenuDown, mdiMenuRight} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import StudentEnrollmentTerm from '@/components/student/profile/StudentEnrollmentTerm'
import Util from '@/mixins/Util'
import {each, groupBy, includes, map, orderBy} from 'lodash'
import {sisIdForTermName} from '@/berkeley'

export default {
  name: 'StudentClasses',
  components: {StudentEnrollmentTerm},
  mixins: [Context, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    currentOrder: undefined,
    panelsExpanded: []
  }),
  computed: {
    enrollmentTermsByYear() {
      const grouped = groupBy(this.student.enrollmentTerms, 'academicYear')
      const enrollmentTermsByYear = map(grouped, (terms, label) => ({label, terms}))
      return orderBy(enrollmentTermsByYear, 'label', this.currentOrder)
    }
  },
  created() {
    this.currentOrder = 'desc'
    const currentEnrollmentTerm = this.config.currentEnrollmentTerm
    each(this.enrollmentTermsByYear, year => {
      const academicYear = [`Fall ${year.label - 1}`, `Spring ${year.label}`, `Summer ${year.label}`]
      if (includes(academicYear, currentEnrollmentTerm)) {
        this.panelsExpanded.push(year.label)
      }
    })
  },
  methods: {
    getTerm(termName, year) {
      const term = this._find(year.terms, {'termName': termName})
      if (!term) {
        return {
          termId: sisIdForTermName(termName),
          termName: termName
        }
      }
      return term
    },
    includesCurrentTerm(year) {
      return this._includes([`Fall ${year.label - 1}`, `Spring ${year.label}`, `Summer ${year.label}`], this.config.currentEnrollmentTerm)
    },
    setOrder() {
      this.currentOrder = this.currentOrder === 'asc' ? 'desc' : 'asc'
      this.alertScreenReader(`The sort order of the academic years has changed to ${this.currentOrder}ending`)
    },
    toggle() {
      const hasSomeExpanded = this.panelsExpanded.length
      this.panelsExpanded = hasSomeExpanded ? [] : map(this.student.enrollmentTerms, 'academicYear')
      this.alertScreenReader(`All academic years have been ${hasSomeExpanded ? 'collapsed' : 'expanded'}`)
    },
    totalUnits(year) {
      return this._sumBy(year.terms, 'enrolledUnits')
    }
  }
}
</script>

<style scoped>
.expansion-panel-icon {
  margin-left: -10px;
}
.student-enrollment-term {
  width: 33.3%;
}
</style>
