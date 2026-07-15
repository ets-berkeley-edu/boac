<template>
  <div class="default-margins">
    <div class="align-baseline d-flex flex-wrap justify-space-between">
      <h1 id="page-header" class="text-no-wrap mr-2">Batch Degree Checks</h1>
      <router-link id="manage-degrees-link" to="/degrees">
        <div class="text-no-wrap">
          Manage degree checks
        </div>
      </router-link>
    </div>
    <div>
      <div aria-live="polite" class="font-italic font-size-14 pb-2 student-count-alerts">
        <span
          v-if="overStudentLimit"
          id="target-student-count-alert"
          class="font-weight-bold text-error"
        >
          {{ studentLimitMessage }}
        </span>
        <span
          v-else-if="!isEmpty(sidsToInclude)"
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
        <label class="font-weight-bold mt-1" for="degree-check-add-sids">Student</label>
        <BulkAddSids
          embedded
          :on-bulk-add-sids="onBulkAddSids"
          heading-id="page-header"
          id-prefix="degree-check-add"
          :is-saving="isBusy"
          :on-esc="onCancel"
          submit-aria-label="Add Students to Degree Check"
        />
        <ul
          v-if="addedStudents.length"
          aria-label="Students added to Degree Check"
          class="mb-2 list-no-bullets pl-0"
        >
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
      <v-alert
        v-if="error"
        aria-live="polite"
        class="mt-2 mb-3 w-75"
        :class="{'w-100': $vuetify.display.xs}"
        density="compact"
        type="error"
        variant="tonal"
      >
        <v-alert-title class="font-size-16">{{ error }}</v-alert-title>
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
        <v-alert-title class="font-size-16">
          {{ pluralize('student', excludedStudents.length) }} currently {{ excludedStudents.length === 1 ? 'uses' : 'use' }} the {{ selectedTemplate.name }} degree check. The degree check will not be added to their student record.
        </v-alert-title>
        <ul aria-label="Students already using this Degree Check" class="ml-5 mt-1 mb-0">
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
          :disabled="isBusy || !selectedTemplate || isEmpty(sidsToInclude) || overStudentLimit"
          :in-progress="isSaving"
          :text="isSaving ? 'Saving' : 'Save Degree Check'"
        />
        <v-btn
          id="batch-degree-check-cancel"
          aria-label="Cancel Create Degree Check"
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
import {computed, nextTick, onMounted, ref, watch} from 'vue'
import {
  filter as _filter,
  difference,
  every,
  get,
  indexOf,
  isEmpty,
  map,
  uniq
} from 'lodash'
import {mdiCloseCircle} from '@mdi/js'
import {useRouter} from 'vue-router'
import BatchAddStudentSet from '@/components/util/BatchAddStudentSet'
import BulkAddSids from '@/components/util/BulkAddSids.vue'
import DegreeTemplatesMenu from '@/components/degree/DegreeTemplatesMenu'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, pluralize, putFocusNextTick} from '@/lib/utils'
import {createBatchDegreeCheck, getStudents} from '@/api/degree'
import {getDistinctSids, getStudentsBySids} from '@/api/student'
import {useContextStore} from '@/stores/context'

const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const router = useRouter()

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

const addedCohortsEmpty = computed(() => addedCohorts.value.length && every(addedCohorts.value, {'totalStudentCount': 0}))
const addedGroupsEmpty = computed(() => addedCuratedGroups.value.length && every(addedCuratedGroups.value, {'totalStudentCount': 0}))
const addedSids = computed(() => map(addedStudents.value, 'sid'))
const isBusy = computed(() => isSaving.value || isValidating.value || isRecalculating.value)
const studentLimit = computed(() => contextStore.config.degreeCheckBatchStudentLimit)
const studentLimitMessage = computed(() => `Sorry, only a maximum total of ${studentLimit.value} students at a time.`)
const sidsToInclude = computed(() => difference(distinctSids.value, map(excludedStudents.value, 'sid')))
const overStudentLimit = computed(() => sidsToInclude.value.length > studentLimit.value)

watch(selectedTemplate, value => {
  findStudentsWithDegreeCheck(value, distinctSids.value)
})
watch(distinctSids, value => {
  findStudentsWithDegreeCheck(selectedTemplate.value, value)
})

contextStore.loadingStart()

onMounted(() => contextStore.loadingComplete())

const clearErrors = () => {
  error.value = null
}

const projectDistinctSids = (sids, cohorts, curatedGroups) => {
  const cohortIds = map(cohorts, 'id')
  const curatedGroupIds = map(curatedGroups, 'id')
  if (cohortIds.length || curatedGroupIds.length) {
    return getDistinctSids(sids, cohortIds, curatedGroupIds).then(data => data.sids)
  }
  return Promise.resolve(uniq(sids))
}

const rejectIfOverLimit = projectedSids => {
  if (projectedSids.length > studentLimit.value) {
    error.value = studentLimitMessage.value
    alertScreenReader(error.value, false, 'assertive')
    return true
  }
  return false
}

const addCohort = cohort => {
  clearErrors()
  const proposedCohorts = [...addedCohorts.value, cohort]
  isRecalculating.value = true
  return projectDistinctSids(addedSids.value, proposedCohorts, addedCuratedGroups.value).then(projected => {
    if (rejectIfOverLimit(projected)) {
      isRecalculating.value = false
      return false
    }
    addedCohorts.value.push(cohort)
    distinctSids.value = projected
    isRecalculating.value = false
    return true
  }).catch(() => {
    isRecalculating.value = false
    return false
  })
}

const addCuratedGroup = curatedGroup => {
  clearErrors()
  const proposedGroups = [...addedCuratedGroups.value, curatedGroup]
  isRecalculating.value = true
  return projectDistinctSids(addedSids.value, addedCohorts.value, proposedGroups).then(projected => {
    if (rejectIfOverLimit(projected)) {
      isRecalculating.value = false
      return false
    }
    addedCuratedGroups.value.push(curatedGroup)
    distinctSids.value = projected
    isRecalculating.value = false
    return true
  }).catch(() => {
    isRecalculating.value = false
    return false
  })
}

const onBulkAddSids = sids => {
  clearErrors()
  isValidating.value = true
  const novelSids = difference(uniq(sids), addedSids.value)
  if (!novelSids.length) {
    isValidating.value = false
    alertScreenReader('No new students to add; those SIDs are already in the list.')
    putFocusNextTick('degree-check-add-sids')
    return true
  }
  const proposedSids = uniq([...addedSids.value, ...novelSids])
  return projectDistinctSids(proposedSids, addedCohorts.value, addedCuratedGroups.value).then(projected => {
    if (rejectIfOverLimit(projected)) {
      isValidating.value = false
      return false
    }
    return getStudentsBySids(novelSids).then(students => {
      addStudents(students)
      isValidating.value = false
      return true
    })
  }).catch(() => {
    isValidating.value = false
    return false
  })
}

const addStudents = students => {
  if (students && students.length) {
    const existing = new Set(addedSids.value)
    const toAdd = students.filter(s => !existing.has(s.sid))
    if (toAdd.length) {
      addedStudents.value.push(...toAdd)
      recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value).then(() => {
        const obj = toAdd.length === 1 ? `${toAdd[0].label}` : pluralize('student', toAdd.length)
        alertScreenReader(`${obj} added to degree check`)
      })
    }
  }
  putFocusNextTick('degree-check-add-sids')
}

const addTemplate = template => {
  selectedTemplate.value = template
  findStudentsWithDegreeCheck()
}

const onCancel = () => {
  alertScreenReader('Canceled. Nothing saved.')
  router.push('/degrees')
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
  return projectDistinctSids(sids, cohorts, curatedGroups).then(projected => {
    distinctSids.value = projected
  }).finally(() => {
    isRecalculating.value = false
  })
}

const removeCohort = cohort => {
  const index = indexOf(addedCohorts.value, cohort)
  if (index !== -1) {
    clearErrors()
    addedCohorts.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
  }
}

const removeCuratedGroup = curatedGroup => {
  const index = indexOf(addedCuratedGroups.value, curatedGroup)
  if (index !== -1) {
    clearErrors()
    addedCuratedGroups.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value)
  }
}

const removeStudent = student => {
  const index = indexOf(addedStudents.value, student)
  if (index !== -1) {
    clearErrors()
    addedStudents.value.splice(index, 1)
    recalculateStudentCount(addedSids.value, addedCohorts.value, addedCuratedGroups.value).then(() => alertScreenReader(`${student.label} removed`))
  }
}

const save = () => {
  if (overStudentLimit.value) {
    error.value = studentLimitMessage.value
    return
  }
  isSaving.value = true
  alertScreenReader('Saving Degree Check.')
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
.student-count-alerts {
  line-height: 1.2rem;
  min-height: 1.2rem;
}
</style>
