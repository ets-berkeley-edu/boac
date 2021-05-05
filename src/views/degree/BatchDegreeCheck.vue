<template>
  <div v-if="!loading" class="ml-3 mr-3 mt-3">
    <h1 class="page-section-header">Batch Degree Checks</h1>
    <div role="alert">
      <span v-if="isRecalculating" />
      <span
        v-if="!isRecalculating && sids.length"
        id="target-student-count-alert"
        :class="{'has-error': sids.length >= 250, 'font-weight-bolder': sids.length >= 500}"
        class="font-italic font-size-14"
      >
        Degree check will be added to {{ pluralize('student record', sids.length) }}.
        <span v-if="sids.length >= 500">Are you sure?</span>
      </span>
      <span
        v-if="!sids.length && (addedCohorts.length || addedCuratedGroups.length)"
        class="font-italic font-size-14"
      >
        <span
          v-if="addedCohorts.length && !addedCuratedGroups.length"
          id="no-students-per-cohorts-alert"
        >There are no students in the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }}.</span>
        <span
          v-if="addedCuratedGroups.length && !addedCohorts.length"
          id="no-students-per-curated-groups-alert"
        >There are no students in the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }}.</span>
        <span
          v-if="addedCohorts.length && addedCuratedGroups.length"
          id="no-students-alert"
        >
          Neither the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }} nor the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }} have students.
        </span>
      </span>
    </div>
    <div>
      <label
        for="degree-check-add-student-input"
        class="font-size-14 input-label text mt-2"
      >
        <div class="font-weight-bolder">Student</div>
        <span>Type a name, individual Student Identification (SID), or paste a list of SID numbers below. Example: 9999999990, 9999999991</span>
      </label>
    </div>
    <div class="mb-2">
      <span id="degree-check-add-student-label" class="sr-only">Select student for degree check. Expect auto-suggest as you type name or SID.</span>
      <Autocomplete
        id="degree-check-add-student"
        :key="resetAutoCompleteKey"
        ref="autocomplete"
        class="w-75"
        :add-selection="addSids"
        :add-button-disabled="(selectedSuggestion, query) => !selectedSuggestion && !/^\d+[,\r\n\t ]+/.test(query)"
        :demo-mode-blur="true"
        :disabled="disabled"
        input-labelled-by="degree-check-add-student-label"
        :maxlength="'255'"
        :show-add-button="true"
        :source="studentsByNameOrSid"
        :suggest-when="query => query && query.length > 1 && !/[,\r\n\t ]+/.test(query)"
        @input="addStudent"
      />
    </div>
    <div>
      <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="mb-1">
        <span class="font-weight-bolder pill pill-attachment text-uppercase text-nowrap truncate">
          <span :id="`batch-note-student-${index}`" :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ addedStudent.label }}</span>
          <b-btn
            :id="`remove-student-from-batch-${index}`"
            variant="link"
            class="p-0"
            @click.prevent="removeStudent(addedStudent)"
          >
            <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
            <span class="sr-only">Remove {{ addedStudent.label }} from degree check</span>
          </b-btn>
        </span>
      </div>
    </div>
    <div v-if="error" class="error-message-container  alert-box p-3 mt-2 mb-3 w-100">
      {{ error }}
    </div>
    <div
      v-if="warnings && warnings.length"
      class="warning-message-container alert-box p-3 mt-2 mb-3 w-100"
    >
      <ul class="mb-0">
        <li v-for="(warning, index) in warnings" :key="index">{{ warning }}</li>
      </ul>
    </div>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import Context from '@/mixins/Context'
import Loading from '@/mixins/Loading'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'

export default {
  name: 'BatchDegreeCheck',
  components: {
    Autocomplete
  },
  mixins: [Context, Loading, Util, Validator],
  data: () => ({
    addedCohorts: [],
    addedCuratedGroups: [],
    addedStudents: [],
    disabled: false,
    error: undefined,
    isRecalculating: false,
    resetAutoCompleteKey: undefined,
    warnings: []
  }),
  computed: {
    sids() {
      return this.$_.map(this.addedStudents, 'sid')
    }
  },
  watch: {
    error(value) {
      if (value) {
        this.$nextTick(() => {
          this.alertScreenReader(value)
        })
      }
    },
    warnings(value) {
      if (value && value.length) {
        this.alertScreenReader(value.join('. '))
      }
    }
  },
  mounted() {
    this.loaded('Batch degree checks')
  },
  methods: {
    addSids(query) {
      return new Promise(resolve => {
        const sids = this.validateSids(query)
        if (sids) {
          const novelSids = this.$_.difference(sids, this.sids)
          if (novelSids.length) {
            getStudentsBySids(novelSids).then(students => {
              this.addStudents(students)
              resolve()
            })
          }
        }
        resolve()
      })
    },
    addStudent(student) {
      if (student) {
        this.addedStudents.push(student)
        this.resetAutoCompleteKey = new Date().getTime()
        this.alertScreenReader(`${student.label} added to degree check`)
        this.clearErrors()
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    addStudents(students) {
      if (students && students.length) {
        this.addedStudents.push(...students)
        this.resetAutoCompleteKey = new Date().getTime()
        this.alertScreenReader(`${this.pluralize('student', students.length)} added to degree check`)
        this.clearErrors()
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    removeStudent(student) {
      if (student) {
        this.addedStudents = this.$_.filter(this.addedStudents, a => a.sid !== student.sid)
        this.alertScreenReader(`${student.label} removed from degree check`)
      }
    },
    studentsByNameOrSid(query, limit) {
      const sids = this.$_.map(this.addedStudents, 'sid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this.$_.filter(students, s => !this.$_.includes(sids, s.sid)))
        })
      })
    }
  }
}
</script>
