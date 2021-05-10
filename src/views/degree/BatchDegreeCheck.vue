<template>
  <div v-if="!loading" class="ml-3 mr-3 mt-3">
    <h1 class="page-section-header">Batch Degree Checks</h1>
    <div role="alert">
      <span v-if="isRecalculating" />
      <span
        v-if="!isRecalculating && distinctSids.length"
        id="target-student-count-alert"
        :class="{'has-error': distinctSids.length >= 250, 'font-weight-bolder': distinctSids.length >= 500}"
        class="font-italic font-size-14"
      >
        Degree check will be added to {{ pluralize('student record', distinctSids.length) }}.
        <span v-if="distinctSids.length >= 500">Are you sure?</span>
      </span>
      <span
        v-if="!isRecalculating && !distinctSids.length && (addedCohorts.length || addedCuratedGroups.length)"
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
        :add-button-disabled="addButtonDisabled"
        :demo-mode-blur="true"
        :disabled="isSaving"
        input-labelled-by="degree-check-add-student-label"
        :maxlength="'255'"
        :show-add-button="true"
        :source="studentsByNameOrSid"
        :suggest-when="suggestWhen"
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
    <div
      v-if="error || warning"
      :class="{'error-message-container': error, 'warning-message-container': warning}"
      class="alert-box p-3 mt-2 mb-3 w-75"
      v-html="error || warning"
    />
    <div class="mb-2">
      <BatchAddStudentSet
        v-if="myCohorts && myCohorts.length"
        class="w-75"
        :add-object="addCohort"
        :disabled="isSaving"
        :is-curated-groups-mode="false"
        :remove-object="removeCohort"
        :target="'degree check'"
      />
    </div>
    <div class="mb-2">
      <BatchAddStudentSet
        v-if="myCuratedGroups && myCuratedGroups.length"
        class="w-75"
        :add-object="addCuratedGroup"
        :disabled="isSaving"
        :is-curated-groups-mode="true"
        :remove-object="removeCuratedGroup"
        :target="'degree check'"
      />
    </div>
    <div class="mb-2">
      <DegreeTemplatesMenu
        class="w-75"
        :disabled="isSaving"
        :on-select="addTemplate"
      />
    </div>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import BatchAddStudentSet from '@/components/util/BatchAddStudentSet'
import Context from '@/mixins/Context'
import CurrentUserExtras from '@/mixins/CurrentUserExtras'
import DegreeTemplatesMenu from '@/components/degree/DegreeTemplatesMenu'
import Loading from '@/mixins/Loading'
import StudentAggregator from '@/mixins/StudentAggregator'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'

export default {
  name: 'BatchDegreeCheck',
  components: {
    Autocomplete,
    BatchAddStudentSet,
    DegreeTemplatesMenu
  },
  mixins: [Context, CurrentUserExtras, Loading, StudentAggregator, Util, Validator],
  data: () => ({
    addedCohorts: [],
    addedCuratedGroups: [],
    addedStudents: [],
    error: undefined,
    isSaving: false,
    isValidating: false,
    resetAutoCompleteKey: undefined,
    templateId: undefined,
    warning: undefined
  }),
  computed: {
    addedSids() {
      return this.$_.map(this.addedStudents, 'sid')
    }
  },
  mounted() {
    this.loaded('Batch degree checks')
  },
  methods: {
    addButtonDisabled(selectedSuggestion, query) {
      !selectedSuggestion && !/^\d+[,\r\n\t ]?/.test(query)
    },
    addCohort(cohort) {
      this.clearErrors()
      this.addedCohorts.push(cohort)
      this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
    },
    addCuratedGroup(curatedGroup) {
      this.clearErrors()
      this.addedCuratedGroups.push(curatedGroup)
      this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
    },
    addSids(query) {
      return new Promise((resolve, reject) => {
        this.isValidating = true
        const sids = this.validateSids(query)
        if (sids) {
          const novelSids = this.$_.difference(sids, this.distinctSids)
          if (novelSids.length) {
            getStudentsBySids(novelSids).then(students => {
              this.addStudents(students)
              const notFound = this.$_.difference(novelSids, this.$_.map(students, 'sid'))
              if (notFound.length === 1) {
                this.warning = `Student ${notFound[0]} not found.`
                this.alertScreenReader(this.warning)
              } else if (notFound.length > 1) {
                this.warning = `${notFound.length} students not found: <ul class="mt-1 mb-0"><li>${this.$_.join(notFound, '</li><li>')}</li></ul>`
                this.alertScreenReader(`${notFound.length} student IDs not found: ${this.oxfordJoin(notFound)}`)
              }
              this.isValidating = false
              resolve()
            })
          }
          else {
            this.isValidating = false
            resolve()
          }
        } else {
          if (this.error) {
            this.alertScreenReader(`Error: ${this.error}`)
          } else if (this.warning) {
            this.alertScreenReader(`Warning: ${this.warning}`)
          }
          this.$nextTick(() => this.isValidating = false)
          reject()
        }
      })
    },
    addStudent(student) {
      if (student) {
        this.addedStudents.push(student)
        this.resetAutoCompleteKey = new Date().getTime()
        this.clearErrors()
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups).then(
          () => this.alertScreenReader(`${student.label} added to degree check`)
        )
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    addStudents(students) {
      if (students && students.length) {
        this.addedStudents.push(...students)
        this.resetAutoCompleteKey = new Date().getTime()
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups).then(
          () => this.alertScreenReader(`${this.pluralize('student', students.length)} added to degree check`)
        )
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    addTemplate(templateId) {
      this.templateId = templateId
    },
    removeCohort(cohort) {
      this.$_.remove(this.addedCohorts, c => c.id === cohort.id),
      this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
    },
    removeCuratedGroup(curatedGroup) {
      this.$_.remove(this.addedCuratedGroups, c => c.id === curatedGroup.id),
      this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
    },
    removeStudent(student) {
      if (student) {
        this.addedStudents = this.$_.filter(this.addedStudents, a => a.sid !== student.sid)
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups).then(() => this.alertScreenReader(`${student.label} removed`))
      }
    },
    studentsByNameOrSid(query, limit) {
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this.$_.filter(students, s => !this.$_.includes(this.addedSids, s.sid)))
        })
      })
    },
    suggestWhen(query) {
      return !this.isValidating && query && query.length > 1 && !/[,\r\n\t ]+/.test(query)
    }
  }
}
</script>
