<template>
  <div class="default-margins">
    <div class="align-items-baseline d-flex flex-wrap justify-space-between">
      <h1 id="page-header" class="text-no-wrap mr-2">Batch Degree Checks</h1>
      <router-link id="manage-degrees-link" to="/degrees">
        <div class="text-no-wrap">
          Manage degree checks
        </div>
      </router-link>
    </div>
    <div>
      <div aria-live="polite" class="font-italic font-size-14 pb-2 student-count-alerts" role="alert">
        <span
          v-if="!isEmpty(sidsToInclude)"
          id="target-student-count-alert"
          :class="{'text-error': sidsToInclude.length >= 250, 'font-weight-bold': sidsToInclude.length >= 500}"
        >
          Degree check will be added to {{ pluralize('student record', sidsToInclude.length) }}.
          <span v-if="sidsToInclude.length >= 500">Are you sure?</span>
        </span>
        <span v-if="isEmpty(sidsToInclude) && (addedCohortsEmpty || addedGroupsEmpty)">
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
      <div class="w-75" :class="{'w-100': $vuetify.display.xs}">
        <label
          for="degree-check-add-student-input"
          class="text mt-1"
        >
          <span class="font-weight-bold">Student</span>
          <br />
          <span class="font-size-14">Type or paste a list of SID numbers below. Example: 9999999990, 9999999991</span>
        </label>
        <div class="pt-2">
          <v-textarea
            id="degree-check-add-student"
            v-model="textarea"
            aria-label="Type or paste a list of student SID numbers here"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
            density="compact"
            :disabled="isBusy"
            :error="!!error"
            hide-details
            max-rows="30"
            rows="8"
            variant="outlined"
            @keydown.esc="onCancel"
            @update:model-value="clearErrors"
          />
        </div>
        <div class="align-start d-flex pt-3 w-100">
          <div>
            <ul v-if="addedStudents.length" class="mb-2 list-no-bullets pl-0">
              <li
                v-for="(addedStudent, index) in addedStudents"
                :key="addedStudent.sid"
                class="added-student-list-item align-center d-flex justify-space-between"
              >
                <div
                  :id="`batch-note-student-${index}`"
                  :class="{'demo-mode-blur': currentUser.inDemoMode}"
                >
                  {{ addedStudent.label }}
                </div>
                <div>
                  <v-btn
                    :id="`remove-student-from-batch-${index}`"
                    class="pr-0"
                    :disabled="isSaving"
                    variant="text"
                    @click="() => removeStudent(addedStudent)"
                  >
                    <v-icon color="error" :icon="mdiCloseCircle" />
                    <span class="sr-only">Remove {{ addedStudent.label }} from degree check</span>
                  </v-btn>
                </div>
              </li>
            </ul>
          </div>
          <div class="ms-auto">
            <v-btn
              id="degree-check-add-sids-btn"
              color="primary"
              :disabled="!trim(textarea) || isBusy || isValidating"
              text="Add"
              variant="flat"
              @click.prevent="addSids"
            />
          </div>
        </div>
      </div>
      <v-alert
        v-if="error || warning"
        aria-live="polite"
        class="mt-2 mb-3 w-75"
        :class="{'w-100': $vuetify.display.xs}"
        density="compact"
        :type="error ? 'error' : 'warning'"
        variant="tonal"
      >
        <v-alert-title class="font-size-16" :class="{'text-warning-darken-1': warning}" v-html="error || warning"></v-alert-title>
        <div v-if="size(sidsInError)">
          <ul id="sids-not-found" class="mb-1 pl-6" :class="{'columns-list': size(sidsInError) > 5}">
            <li v-for="(sid, index) in sidsInError" :key="index">{{ sid }}</li>
          </ul>
        </div>
      </v-alert>
      <div class="pb-2">
        <BatchAddStudentSet
          v-if="currentUser.myCohorts.length"
          :add-object="addCohort"
          class="w-75"
          :class="{'w-100': $vuetify.display.xs}"
          :disabled="isSaving"
          header="Cohort"
          :objects="currentUser.myCohorts"
          object-type="cohort"
          :remove-object="removeCohort"
        />
      </div>
      <div class="pb-3">
        <BatchAddStudentSet
          v-if="currentUser.myCuratedGroups.length"
          :add-object="addCuratedGroup"
          class="w-75"
          :class="{'w-100': $vuetify.display.xs}"
          :disabled="isSaving"
          header="Curated Group"
          :objects="_filter(currentUser.myCuratedGroups, ['domain', 'default'])"
          object-type="curated"
          :remove-object="removeCuratedGroup"
        />
      </div>
      <div class="pb-3 w-75" :class="{'w-100': $vuetify.display.xs}">
        <DegreeTemplatesMenu
          :disabled="isSaving"
          :on-select="addTemplate"
        />
      </div>
      <v-alert
        v-if="!isRecalculating && !isValidating && !isEmpty(excludedStudents)"
        aria-live="polite"
        class="mt-2 mb-3 w-75"
        :class="{'w-100': $vuetify.display.xs}"
        density="compact"
        type="warning"
        variant="tonal"
      >
        <v-alert-title class="font-size-16 text-warning-darken-1">
          {{ pluralize('student', excludedStudents.length) }} currently {{ excludedStudents.length === 1 ? 'uses' : 'use' }} the {{ selectedTemplate.name }} degree check. The degree check will not be added to their student record.
        </v-alert-title>
        <ul class="ml-5 mt-1 mb-0">
          <li
            v-for="(student, index) in excludedStudents"
            :key="index"
            :class="{'demo-mode-blur': currentUser.inDemoMode}"
          >
            {{ student.firstName }} {{ student.lastName }} ({{ student.sid }})
          </li>
        </ul>
      </v-alert>
      <div class="d-flex pt-2 w-75" :class="{'w-100': $vuetify.display.xs}">
        <ProgressButton
          id="batch-degree-check-save"
          :action="save"
          class="ms-auto mr-2"
          color="primary"
          :disabled="isBusy || !selectedTemplate || isEmpty(sidsToInclude)"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving' : 'Save Degree Check'"
        />
        <v-btn
          id="batch-degree-check-cancel"
          color="primary"
          :disabled="isBusy"
          text="Cancel"
          variant="text"
          @click="onCancel"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import BatchAddStudentSet from '@/components/util/BatchAddStudentSet'
import DegreeTemplatesMenu from '@/components/degree/DegreeTemplatesMenu'
import ProgressButton from '@/components/util/ProgressButton'
import router from '@/router'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {computed, nextTick, onMounted, ref, watch} from 'vue'
import {createBatchDegreeCheck, getStudents} from '@/api/degree'
import {
  difference,
  every,
  filter as _filter,
  get,
  indexOf,
  isEmpty,
  map,
  partition,
  size,
  split,
  trim,
  uniq
} from 'lodash'
import {getDistinctSids, getStudentsBySids} from '@/api/student'
import {mdiCloseCircle} from '@mdi/js'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser

const addedCohorts = ref([])
const addedCuratedGroups = ref([])
const addedStudents = ref([])
const distinctSids = ref([])
const error = ref(undefined)
const excludedStudents = ref([])
const isRecalculating = ref(false)
const isSaving = ref(false)
const isValidating = ref(false)
const selectedTemplate = ref(undefined)
const sidsInError = ref([])
const textarea = ref(undefined)
const warning = ref(undefined)

const addedCohortsEmpty = computed(() => addedCohorts.value.length && every(addedCohorts.value, {'totalStudentCount': 0}))
const addedGroupsEmpty = computed(() => addedCuratedGroups.value.length && every(addedCuratedGroups.value, {'totalStudentCount': 0}))
const addedSids = computed(() => map(addedStudents.value, 'sid'))
const isBusy = computed(() => isSaving.value || isValidating.value || isRecalculating.value)

const sidsToInclude = computed(() => difference(distinctSids.value, map(excludedStudents.value, 'sid')))

watch(selectedTemplate, value => {
  findStudentsWithDegreeCheck(value, distinctSids.value)
})
watch(distinctSids, value => {
  findStudentsWithDegreeCheck(selectedTemplate.value, value)
})

onMounted(() => alertScreenReader('Batch degree checks loaded'))

const addCohort = cohort => {
  clearErrors()
  addedCohorts.value.push(cohort)
  recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
}

const addCuratedGroup = curatedGroup => {
  clearErrors()
  addedCuratedGroups.value.push(curatedGroup)
  recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
}

const addSids = () => {
  return new Promise((resolve, reject) => {
    isValidating.value = true
    const sids = validateSids(textarea.value)
    if (sids) {
      const uniqueSids = uniq(sids)
      getStudentsBySids(uniqueSids).then(students => {
        addStudents(students)
        const notFound = difference(uniqueSids, map(students, 'sid'))
        if (notFound.length === 1) {
          warning.value = `Student ${notFound[0]} not found.`
          alertScreenReader(warning.value)
        } else if (notFound.length > 1) {
          warning.value = `${notFound.length} students not found:`
          sidsInError.value = notFound
        }
        isValidating.value = false
        textarea.value = undefined
        resolve()
      })
    } else {
      if (error.value) {
        alertScreenReader(`Error: ${error.value}`)
      } else if (warning.value) {
        alertScreenReader(`Warning: ${warning.value}`)
      }
      nextTick(() => isValidating.value = false)
      reject()
    }
  })
}

const addStudents = students => {
  if (students && students.length) {
    addedStudents.value.push(...students)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value).then( () => {
      const obj = students.length === 1 ? `${students[0].label}` : pluralize('student', students.length)
      alertScreenReader(`${obj} added to degree check`)
    })
  }
  putFocusNextTick('degree-check-add-student-input')
}

const addTemplate = template => {
  selectedTemplate.value = template
  findStudentsWithDegreeCheck()
}

const onCancel = () => {
  alertScreenReader('Canceled. Nothing saved.')
  router.push('/degrees')
}

const clearErrors = () => {
  error.value = null
  sidsInError.value = []
  warning.value = null
}

const findStudentsWithDegreeCheck = (selectedTemplate, sids) => {
  if (get(selectedTemplate, 'id') && !isEmpty(sids)) {
    isValidating.value = true
    getStudents(selectedTemplate.id, sids).then(students => {
      excludedStudents.value = students
      isValidating.value = false
    })
  } else {
    excludedStudents.value = []
  }
}

const recalculateStudentCount = (sids, cohorts, curatedGroups) => {
  isRecalculating.value = true
  return new Promise(resolve => {
    const cohortIds = map(cohorts, 'id')
    const curatedGroupIds = map(curatedGroups, 'id')
    if (cohortIds.length || curatedGroupIds.length) {
      getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => {
        distinctSids.value = data.sids
      }).finally(() => {
        isRecalculating.value = false
        resolve()
      })
    } else {
      distinctSids.value = uniq(sids)
      isRecalculating.value = false
      resolve()
    }
  })
}

const removeCohort = cohort => {
  const index = indexOf(addedCohorts.value, cohort)
  if (index !== -1) {
    addedCohorts.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
  }
}

const removeCuratedGroup = curatedGroup => {
  const index = indexOf(addedCuratedGroups.value, curatedGroup)
  if (index !== -1) {
    addedCuratedGroups.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
  }
}

const removeStudent = student => {
  const index = indexOf(addedStudents.value, student)
  if (index !== -1) {
    addedStudents.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value).then(() => alertScreenReader(`${student.label} removed`))
  }
}

const save = () => {
  isSaving.value = true
  alertScreenReader('Saving.')
  createBatchDegreeCheck(sidsToInclude.value, get(selectedTemplate.value, 'id')).then(() => {
    nextTick(() => {
      router.push({
        path: '/degrees',
        query: {
          m: `Degree check ${selectedTemplate.value.name} added to ${pluralize('student profile', sidsToInclude.value.length)}.`
        }
      }).then(() => {
        isSaving.value = false
      })
    })
  })
}

const validateSids = sids => {
  clearErrors()
  const trimmed = trim(sids, ' ,\n\t')
  if (trimmed) {
    const splitted = split(trimmed, /[,\r\n\t ]+/)
    if (splitted.length && splitted[0].length > 10) {
      error.value = 'SIDs must be separated by commas, line breaks, or tabs.'
      return false
    }
    const notNumeric = partition(splitted, sid => /^\d+$/.test(trim(sid)))[1]
    if (notNumeric.length) {
      error.value = 'Each SID must be numeric.'
    } else {
      return splitted
    }
  } else {
    warning.value = 'Please provide one or more SIDs.'
  }
  return false
}
</script>

<style scoped>
.added-student-list-item {
  background-color: rgba(var(--v-theme-surface));
  border-radius: 5px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  color: rgba(var(--v-theme-on-surface), var(--v-medium-emphasis-opacity));
  display: inline-block;
  height: 36px;
  margin-top: 6px;
  padding: 2px 0 0 8px;
  min-width: 50%;
}
.columns-list {
  columns: 2;
}
.student-count-alerts {
  line-height: 1.2rem;
  min-height: 1.2rem;
}
</style>
