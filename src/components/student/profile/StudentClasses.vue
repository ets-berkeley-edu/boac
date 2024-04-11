<template>
  <div id="student-terms-container" class="ma-3 pa-0">
    <div class="align-center d-flex mb-2 px-2">
      <div class="pt-1">
        <h2 class="student-section-header mr-2">Classes</h2>
      </div>
      <div>
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="toggle-collapse-all-years"
          variant="text"
          @click="toggle"
        >
          <v-icon v-if="panelsExpanded.length" :icon="mdiMenuDown" />
          <v-icon v-if="!panelsExpanded.length" :icon="mdiMenuRight" />
          {{ panelsExpanded.length ? 'Collapse' : 'Expand' }} all years
        </v-btn>
      </div>
      <div v-if="enrollmentTermsByYear.length > 1">|</div>
      <div class="flex-grow-1">
        <v-btn
          v-if="enrollmentTermsByYear.length > 1"
          id="sort-academic-year"
          variant="text"
          @click="setOrder"
        >
          Sort academic year
          <span v-if="currentOrder === 'desc' ">
            <v-icon :icon="mdiArrowDownThin" />
          </span>
          <span v-if="currentOrder === 'asc' ">
            <v-icon :icon="mdiArrowUpThin" />
          </span>
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
    <v-expansion-panels v-model="panelsExpanded" multiple>
      <v-expansion-panel
        v-for="year in enrollmentTermsByYear"
        :id="`academic-year-${year.label}-container`"
        :key="year.label"
        :value="year.label"
      >
        <v-expansion-panel-title>
          <div class="d-flex justify-space-between">
            <h3 class="page-section-header-sub ma-0">{{ `Fall ${year.label - 1} - Summer ${year.label}` }}</h3>
            <div class="color-black">{{ totalUnits(year) || 0 }} Units</div>
          </div>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-card>
            <StudentEnrollmentTerm
              :id="`term-fall-${year.label - 1}`"
              :student="student"
              :term="getTerm(`Fall ${year.label - 1}`, year)"
            /><StudentEnrollmentTerm
              :id="`term-spring-${year.label}`"
              :student="student"
              :term="getTerm(`Spring ${year.label}`, year)"
            /><StudentEnrollmentTerm
              :id="`term-summer-${year.label}`"
              :student="student"
              :term="getTerm(`Summer ${year.label}`, year)"
            />
          </v-card>
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
import {map} from 'lodash'
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
      const enrollmentTermsByYear = this._map(
        this._groupBy(this.student.enrollmentTerms, 'academicYear'),
        (terms, label) => {
          return {
            label: label,
            terms: terms
          }
        }
      )
      return this._orderBy(enrollmentTermsByYear, 'label', this.currentOrder)
    },
  },
  created() {
    this.currentOrder = 'desc'
  },
  methods: {
    includesCurrentTerm(year) {
      return this._includes([`Fall ${year.label - 1}`, `Spring ${year.label}`, `Summer ${year.label}`], this.config.currentEnrollmentTerm)
    },
    getDegreeCheckPath() {
      const currentDegreeCheck = this._find(this.student.degreeChecks, 'isCurrent')
      if (currentDegreeCheck) {
        return `/student/degree/${currentDegreeCheck.id}`
      } else if (this.currentUser.canEditDegreeProgress) {
        return `${this.studentRoutePath(this.student.uid, this.currentUser.inDemoMode)}/degree/create`
      } else {
        return `${this.studentRoutePath(this.student.uid, this.currentUser.inDemoMode)}/degree/history`
      }
    },
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
    totalUnits(year) {
      return this._sumBy(year.terms, 'enrolledUnits')
    },
    setOrder() {
      this.currentOrder = this.currentOrder === 'asc' ? 'desc' : 'asc'
      this.alertScreenReader(`The sort order of the academic years has changed to ${this.currentOrder}ending`)
    },
    toggle() {
      this.panelsExpanded = this.panelsExpanded.length ? [] : map(this.student.enrollmentTerms, 'academicYear')
    }
    // updateCollapseStates() {
    //   this.collapsed = this._filter(this.$refs, year => !year[0].$data.show).map(year => year[0].id)
    //   this.uncollapsed = this._filter(this.$refs, year => year[0].$data.show).map(year => year[0].id)
    //   this.expanded = !this.expanded
    //   this.alertScreenReader(`All of the academic years have been ${this.expanded ? 'collapsed' : 'expanded'}`)
    // }
  }
}
</script>

<style>
.profile-boxplot-container {
  align-items: flex-end;
  display: flex;
}
.profile-boxplot-container .highcharts-tooltip {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  line-height: 1.4em;
  min-width: 200px;
  padding: 0;
}
.profile-boxplot-container .highcharts-tooltip::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 1px 1px 0;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  top: 75px;
  left: -6px;
  transform: rotate(135deg);
  width: 10px;
}
.profile-boxplot-container g.highcharts-tooltip {
  display: none !important;
}
.profile-boxplot-container .highcharts-tooltip span {
  position: relative !important;
  top: 0 !important;
  left: 0 !important;
  width: auto !important;
}
</style>

<style scoped>
.background-light {
  background-color: #f9f9f9;
}
.collapsed .when-academic-year-closed,
.not-collapsed .when-academic-year-open {
  display: none;
}
.color-black {
  color: #000;
}
.profile-academic-year-toggle {
  margin-bottom: 15px;
  padding: 10px;
}
</style>
