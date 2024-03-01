<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div class="d-flex flex-wrap align-items-baseline justify-content-between">
      <h1 id="page-header" class="page-section-header text-nowrap mr-2">Batch Degree Checks</h1>
      <router-link id="manage-degrees-link" to="/degrees">
        <div class="text-nowrap">
          Manage degree checks
        </div>
      </router-link>
    </div>
    <div v-if="!loading">
      <div aria-live="polite" class="font-italic font-size-14 student-count-alerts" role="alert">
        <span
          v-if="!_isEmpty(sidsToInclude)"
          id="target-student-count-alert"
          :class="{'has-error': sidsToInclude.length >= 250, 'font-weight-bolder': sidsToInclude.length >= 500}"
        >
          Degree check will be added to {{ pluralize('student record', sidsToInclude.length) }}.
          <span v-if="sidsToInclude.length >= 500">Are you sure?</span>
        </span>
        <span v-if="_isEmpty(sidsToInclude) && (addedCohortsEmpty || addedGroupsEmpty)">
          <span v-if="addedCohortsEmpty && !addedGroupsEmpty" id="no-students-per-cohorts-alert">
            There are no students in the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }}.
          </span>
          <span v-if="!addedCohortsEmpty && addedGroupsEmpty" id="no-students-per-curated-groups-alert">
            There are no students in the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }}.
          </span>
          <span v-if="addedCohortsEmpty && addedGroupsEmpty" id="no-students-alert">
            Neither the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }} nor the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }} have students.
          </span>
        </span>
      </div>
      <div class="w-75">
        <label
          for="degree-check-add-student-input"
          class="input-label text mt-1"
        >
          <div class="font-weight-bolder">Student</div>
          <span class="font-size-14">Type or paste a list of SID numbers below. Example: 9999999990, 9999999991</span>
        </label>
        <div class="mb-2">
          <b-form-textarea
            id="degree-check-add-student"
            v-model="textarea"
            :disabled="isBusy"
            aria-label="Type or paste a list of student SID numbers here"
            rows="8"
            max-rows="30"
            @keydown.esc="cancel"
          ></b-form-textarea>
        </div>
        <div class="d-flex justify-content-end">
          <b-btn
            id="degree-check-add-sids-btn"
            class="btn-primary-color-override"
            :disabled="!_trim(textarea) || isBusy"
            variant="primary"
            @click="addSids"
          >
            <span v-if="isValidating"><v-progress-circular size="small" /> <span class="pl-1">Adding</span></span>
            <span v-if="!isValidating">Add</span>
          </b-btn>
        </div>
        <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="mb-3">
          <span class="font-weight-bolder truncate pill pill-attachment text-uppercase text-nowrap pl-2">
            <span :id="`batch-note-student-${index}`" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ addedStudent.label }}</span>
            <b-btn
              :id="`remove-student-from-batch-${index}`"
              variant="link"
              class="p-0"
              :disabled="isSaving"
              @click.prevent="removeStudent(addedStudent)"
            >
              <v-icon :icon="mdiCloseCircleOutline" class="font-size-20 has-error pl-2" />
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
          v-if="currentUser.myCohorts.length"
          :add-object="addCohort"
          class="w-75"
          :disabled="isSaving"
          header="Cohort"
          :objects="currentUser.myCohorts"
          object-type="cohort"
          :remove-object="removeCohort"
        />
      </div>
      <div class="mb-2">
        <BatchAddStudentSet
          v-if="currentUser.myCuratedGroups.length"
          :add-object="addCuratedGroup"
          class="w-75"
          :disabled="isSaving"
          header="Curated Group"
          :objects="_filter(currentUser.myCuratedGroups, ['domain', 'default'])"
          object-type="curated"
          :remove-object="removeCuratedGroup"
        />
      </div>
      <div class="mb-3">
        <DegreeTemplatesMenu
          class="w-75"
          :disabled="isSaving"
          :on-select="addTemplate"
        />
      </div>
      <div
        v-if="!isRecalculating && !isValidating && !_isEmpty(excludedStudents)"
        class="alert-box warning-message-container p-3 mt-2 mb-3 w-75"
        role="alert"
      >
        <div>{{ excludedStudents.length }} students currently use the {{ selectedTemplate.name }} degree check. The degree check will not be added to their student record.</div>
        <ul class="mt-1 mb-0">
          <li v-for="(student, index) in excludedStudents" :key="index">
            {{ student.firstName }} {{ student.lastName }} ({{ student.sid }})
          </li>
        </ul>
      </div>
      <div class="d-flex justify-content-end pt-2 w-75">
        <b-btn
          id="batch-degree-check-save"
          class="btn-primary-color-override"
          :disabled="isBusy || !selectedTemplate || _isEmpty(sidsToInclude)"
          variant="primary"
          @click="save"
        >
          <span v-if="isSaving"><v-progress-circular class="mr-1" size="small" /> Saving</span>
          <span v-if="!isSaving">Save Degree Check</span>
        </b-btn>
        <b-btn
          id="batch-degree-check-cancel"
          class="pr-0"
          :disabled="isBusy"
          variant="link"
          @click.prevent="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script setup>
import {mdiCloseCircleOutline} from '@mdi/js'
</script>

<script>
import BatchAddStudentSet from '@/components/util/BatchAddStudentSet'
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import DegreeTemplatesMenu from '@/components/degree/DegreeTemplatesMenu'
import Spinner from '@/components/util/Spinner'
import Util from '@/mixins/Util'
import {createBatchDegreeCheck, getStudents} from '@/api/degree'
import {getDistinctSids, getStudentsBySids} from '@/api/student'

export default {
  name: 'BatchDegreeCheck',
  components: {
    BatchAddStudentSet,
    DegreeTemplatesMenu,
    Spinner
  },
  mixins: [Context, DegreeEditSession, Util],
  data: () => ({
    addedCohorts: [],
    addedCuratedGroups: [],
    addedStudents: [],
    distinctSids: [],
    error: undefined,
    excludedStudents: [],
    isRecalculating: false,
    isSaving: false,
    isValidating: false,
    selectedTemplate: undefined,
    textarea: undefined,
    warning: undefined
  }),
  computed: {
    addedCohortsEmpty() {
      return this.addedCohorts.length && this._every(this.addedCohorts, {'totalStudentCount': 0})
    },
    addedGroupsEmpty() {
      return this.addedCuratedGroups.length && this._every(this.addedCuratedGroups, {'totalStudentCount': 0})
    },
    addedSids() {
      return this._map(this.addedStudents, 'sid')
    },
    isBusy() {
      return this.isSaving || this.isValidating || this.isRecalculating
    },
    sidsToInclude() {
      const sidsToExclude = this._map(this.excludedStudents, 'sid')
      return this._difference(this.distinctSids, sidsToExclude)
    }
  },
  watch: {
    selectedTemplate(newValue) {
      this.findStudentsWithDegreeCheck(newValue, this.distinctSids)
    },
    distinctSids(newValue) {
      this.findStudentsWithDegreeCheck(this.selectedTemplate, newValue)
    }
  },
  mounted() {
    this.loadingComplete()
    this.alertScreenReader('Batch degree checks loaded')
  },
  methods: {
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
    addSids() {
      return new Promise((resolve, reject) => {
        this.isValidating = true
        const sids = this.validateSids(this.textarea)
        if (sids) {
          const uniqueSids = this._uniq(sids)
          getStudentsBySids(uniqueSids).then(students => {
            this.addStudents(students)
            const notFound = this._difference(uniqueSids, this._map(students, 'sid'))
            if (notFound.length === 1) {
              this.warning = `Student ${notFound[0]} not found.`
              this.alertScreenReader(this.warning)
            } else if (notFound.length > 1) {
              this.warning = `${notFound.length} students not found: <ul class="mt-1 mb-0"><li>${this._join(notFound, '</li><li>')}</li></ul>`
              this.alertScreenReader(`${notFound.length} student IDs not found: ${this.oxfordJoin(notFound)}`)
            }
            this.isValidating = false
            this.textarea = undefined
            resolve()
          })
        } else {
          if (this.error) {
            this.alertScreenReader(`Error: ${this.error}`)
          } else if (this.warning) {
            this.alertScreenReader(`Warning: ${this.warning}`)
          }
          this.nextTick(() => this.isValidating = false)
          reject()
        }
      })
    },
    addStudents(students) {
      if (students && students.length) {
        this.addedStudents.push(...students)
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups).then( () => {
          const obj = students.length === 1 ? `${students[0].label}` : this.pluralize('student', students.length)
          this.alertScreenReader(`${obj} added to degree check`)
        })
      }
      this.putFocusNextTick('degree-check-add-student-input')
    },
    addTemplate(template) {
      this.selectedTemplate = template
      this.findStudentsWithDegreeCheck()
    },
    cancel() {
      this.alertScreenReader('Canceled. Nothing saved.')
      this.$router.push('/degrees')
    },
    clearErrors() {
      this.error = null
      this.warning = null
    },
    findStudentsWithDegreeCheck(selectedTemplate, sids) {
      if (this._get(selectedTemplate, 'id') && !this._isEmpty(sids)) {
        this.isValidating = true
        getStudents(selectedTemplate.id, sids).then(students => {
          this.excludedStudents = students
          this.isValidating = false
        })
      } else {
        this.excludedStudents = []
      }
    },
    recalculateStudentCount(sids, cohorts, curatedGroups) {
      this.isRecalculating = true
      return new Promise(resolve => {
        const cohortIds = this._map(cohorts, 'id')
        const curatedGroupIds = this._map(curatedGroups, 'id')
        if (cohortIds.length || curatedGroupIds.length) {
          getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => {
            this.distinctSids = data.sids
          }).finally(() => {
            this.isRecalculating = false
            resolve()
          })
        } else {
          this.distinctSids = this._uniq(sids)
          this.isRecalculating = false
          resolve()
        }
      })
    },
    removeCohort(cohort) {
      const index = this._indexOf(this.addedCohorts, cohort)
      if (index !== -1) {
        this.addedCohorts.splice(index, 1)
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
      }
    },
    removeCuratedGroup(curatedGroup) {
      const index = this._indexOf(this.addedCuratedGroups, curatedGroup)
      if (index !== -1) {
        this.addedCuratedGroups.splice(index, 1)
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups)
      }
    },
    removeStudent(student) {
      const index = this._indexOf(this.addedStudents, student)
      if (index !== -1) {
        this.addedStudents.splice(index, 1)
        this.recalculateStudentCount(this.addedSids, this.addedCohorts, this.addedCuratedGroups).then(() => this.alertScreenReader(`${student.label} removed`))
      }
    },
    save() {
      this.isSaving = true
      this.alertScreenReader('Saving.')
      createBatchDegreeCheck(this.sidsToInclude, this._get(this.selectedTemplate, 'id')).then(() => {
        this.nextTick(() => {
          this.$router.push({
            path: '/degrees',
            query: {
              m: `Degree check ${this.selectedTemplate.name} added to ${this.pluralize('student profile', this.sidsToInclude.length)}.`
            }
          })
        })
      }).finally(() => {
        this.isSaving = false
      })
    },
    validateSids: function(sids) {
      this.clearErrors()
      const trimmed = this._trim(sids, ' ,\n\t')
      if (trimmed) {
        const split = this._split(trimmed, /[,\r\n\t ]+/)
        if (split.length && split[0].length > 10) {
          this.error = 'SIDs must be separated by commas, line breaks, or tabs.'
          return false
        }
        const notNumeric = this._partition(split, sid => /^\d+$/.test(this._trim(sid)))[1]
        if (notNumeric.length) {
          this.error = 'Each SID must be numeric.'
        } else {
          return split
        }
      } else {
        this.warning = 'Please provide one or more SIDs.'
      }
      return false
    }
  }
}
</script>

<style scoped>
.student-count-alerts {
  line-height: 1.2rem;
  min-height: 1.2rem;
}
</style>
