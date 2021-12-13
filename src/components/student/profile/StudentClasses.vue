<template>
  <div id="student-terms-container" class="m-3 p-0">
    <div class="align-items-center d-flex mb-2 px-2">
      <div class="pt-1">
        <h2 class="student-section-header mr-2">Classes</h2>
      </div>
      <div>
        <b-button
          v-if="enrollmentTermsByYear.length > 1"
          id="toggle-collapse-all-years"
          v-b-toggle="expanded ? collapsed : uncollapsed"
          variant="link"
          @click="updateCollapseStates"
        >
          <font-awesome v-if="expanded" icon="caret-down" />
          <font-awesome v-if="!expanded" icon="caret-right" />
          {{ expanded ? 'Collapse' : 'Expand' }} all years
        </b-button>
      </div>
      <div v-if="enrollmentTermsByYear.length > 1">|</div>
      <div class="flex-grow-1">
        <b-button
          v-if="enrollmentTermsByYear.length > 1"
          id="sort-academic-year"
          variant="link"
          @click="setOrder"
        >
          Sort academic year
          <span v-if="currentOrder === 'desc' ">
            <font-awesome icon="long-arrow-alt-down" />
          </span>
          <span v-if="currentOrder === 'asc' ">
            <font-awesome icon="long-arrow-alt-up" />
          </span>
        </b-button>
      </div>
      <div v-if="$currentUser.canReadDegreeProgress" class="flex-shrink-1">
        <b-btn
          id="view-degree-check-btn"
          class="pr-0"
          variant="link"
          @click="viewDegreeChecks"
        >
          Degree Checks<span class="sr-only"> of {{ student.name }}</span>
        </b-btn>
      </div>
    </div>
    <div
      v-for="year in enrollmentTermsByYear"
      :id="`academic-year-${year.label}-container`"
      :key="year.label"
    >
      <b-button
        :id="`academic-year-${year.label}-toggle`"
        v-b-toggle="`academic-year-${year.label}`"
        block
        class="profile-academic-year-toggle background-light"
        :pressed="null"
        variant="link"
      >
        <div class="d-flex justify-content-between">
          <div class="align-items-start d-flex">
            <div class="pr-3">
              <font-awesome icon="caret-right" class="when-academic-year-open" />
              <font-awesome icon="caret-down" class="when-academic-year-closed" />
            </div>
            <h3 class="page-section-header-sub m-0">{{ `Fall ${year.label - 1} - Summer ${year.label}` }}</h3>
          </div>
          <div class="align-items-center d-flex justify-content-end">
            <span class="color-black">{{ totalUnits(year) || 0 }} Units</span>
          </div>
        </div>
      </b-button>
      <b-collapse
        :id="`academic-year-${year.label}`"
        :ref="`academic-year-${year.label}`"
        class="mr-3 mb-2 w-100"
        :visible="includesCurrentTerm(year)"
      >
        <b-card-group deck class="d-flex flex-column flex-xl-row m-0">
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
        </b-card-group>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import StudentAnalytics from '@/mixins/StudentAnalytics'
import StudentEnrollmentTerm from '@/components/student/profile/StudentEnrollmentTerm'
import Util from '@/mixins/Util'

export default {
  name: 'StudentClasses',
  components: {
    StudentEnrollmentTerm
  },
  mixins: [Berkeley, Context, StudentAnalytics, Util],
  props: {
    student: Object
  },
  data: () => ({
    currentOrder: undefined,
    expanded: undefined,
    collapsed: [],
    uncollapsed: []
  }),
  created() {
    this.currentOrder = 'desc'
    this.expanded = false
  },
  computed: {
    enrollmentTermsByYear() {
      const enrollmentTermsByYear = this.$_.map(
        this.$_.groupBy(this.student.enrollmentTerms, 'academicYear'),
        (terms, label) => {
          return {
            label: label,
            terms: terms
          }
        }
      )
      return this.$_.orderBy(enrollmentTermsByYear, 'label', this.currentOrder)
    },
  },
  methods: {
    includesCurrentTerm(year) {
      return this.$_.includes([`Fall ${year.label - 1}`, `Spring ${year.label}`, `Summer ${year.label}`], this.$config.currentEnrollmentTerm)
    },
    getTerm(termName, year) {
      const term = this.$_.find(year.terms, {'termName': termName})
      if (!term) {
        return {
          termId: this.sisIdForTermName(termName),
          termName: termName
        }
      }
      return term
    },
    totalUnits(year) {
      return this.$_.sumBy(year.terms, 'enrolledUnits')
    },
    setOrder() {
      this.currentOrder = this.currentOrder === 'asc' ? 'desc' : 'asc'
      this.$announcer.polite(`The sort order of the academic years has changed to ${this.currentOrder}ending`)
    },
    updateCollapseStates() {
      this.collapsed = this.$_.filter(this.$refs, year => !year[0].$data.show).map(year => year[0].id)
      this.uncollapsed = this.$_.filter(this.$refs, year => year[0].$data.show).map(year => year[0].id)
      this.expanded = !this.expanded
      this.$announcer.polite(`All of the academic years have been ${this.expanded ? 'collapsed' : 'expanded'}`)
    },
    viewDegreeChecks() {
      const currentDegreeCheck = this.$_.find(this.student.degreeChecks, 'isCurrent')
      if (currentDegreeCheck) {
        this.$router.push({path: `/student/degree/${currentDegreeCheck.id}`})
      } else if (this.$currentUser.canEditDegreeProgress) {
        this.$router.push({path: `${this.studentRoutePath(this.student.uid, this.$currentUser.inDemoMode)}/degree/create`})
      } else {
        this.$router.push({path: `${this.studentRoutePath(this.student.uid, this.$currentUser.inDemoMode)}/degree/history`})
      }
    }
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
