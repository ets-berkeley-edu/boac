<template>
  <div>
    <div
      v-if="!includes(degreeStore.dismissedAlerts, degreeStore.templateId) && showRevisionIndicator"
      id="revision-warning"
      class="align-center bg-pale-yellow text-gold border-b-sm d-flex mb-3 pb-3 pt-4 px-4"
    >
      <div class="d-inline-block pr-2 w-100">
        <span class="font-weight-bold">Note:</span> Revisions to the
        <router-link
          id="original-degree-template"
          target="_blank"
          :to="`/degree/${degreeStore.parentTemplateId}`"
        >
          original degree template <v-icon :icon="mdiOpenInNew" class="pr-1" size="small" />
          <span class="sr-only"> (will open new browser tab)</span>
        </router-link>
        have been made since the creation of <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}'s</span>
        degree check. Please update below if necessary.
      </div>
      <div class="align-self-center pr-1 pt-1">
        <v-btn
          id="dismiss-alert"
          aria-label="Dismiss alert"
          class="bg-transparent text-primary"
          density="comfortable"
          flat
          :icon="mdiCloseThick"
          size="small"
          title="Dismiss"
          @click="degreeStore.dismissAlert(degreeStore.templateId)"
        />
      </div>
    </div>
    <v-container class="ml-3 mr-6 pb-0" fluid>
      <v-row no-gutters>
        <v-col cols="12" md="7">
          <h2 id="degree-check-header" class="font-size-20 page-section-header">{{ degreeStore.degreeName }}</h2>
          <div class="text-surface-variant font-size-16 font-weight-500 pb-2">
            {{ updatedAtDescription }}
          </div>
        </v-col>
        <v-col class="pr-3" cols="12" md="5">
          <div class="align-baseline d-flex flex-wrap justify-end">
            <div class="pr-2">
              <router-link
                id="print-degree-plan"
                target="_blank"
                :to="`/degree/${degreeStore.templateId}/print?includeNote=${degreeStore.includeNotesWhenPrint}`"
              >
                <v-icon :aria-hidden="true" :icon="mdiPrinter" />
                Print
                <span class="sr-only">this page (will open new browser tab)</span>
              </router-link>
            </div>
            <div class="pr-2">
              |
            </div>
            <div class="pr-2">
              <router-link
                id="view-degree-history"
                :to="`${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/history`"
              >
                History
              </router-link>
            </div>
            <div v-if="currentUser.canEditDegreeProgress" class="pr-2">
              |
            </div>
            <div v-if="currentUser.canEditDegreeProgress" class="pr-2">
              <router-link
                id="create-new-degree"
                :to="`${studentRoutePath(student.uid, currentUser.inDemoMode)}/degree/create`"
              >
                Create New Degree
              </router-link>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row align="start" class="mt-0 pb-3">
        <v-col
          aria-labelledby="degree-notes-header"
          class="align-self-stretch"
          :class="{'border-e-sm': $vuetify.display.mdAndUp}"
          role="region"
        >
          <div class="align-center d-flex flex-wrap justify-space-between">
            <h3 id="degree-notes-header" class="font-size-20 mr-3 pr-2 text-medium-emphasis text-no-wrap">Degree Notes</h3>
            <label v-if="isEditingNote || noteBody" for="degree-note-print-toggle" class="align-center d-flex flex-grow-1 justify-end pr-2">
              <span class="font-size-14 font-weight-500 text-no-wrap text-surface-variant">
                Show notes when printed?
              </span>
              <span
                class="align-center d-flex pl-2"
                :class="{'text-success': degreeStore.includeNotesWhenPrint, 'text-error': !degreeStore.includeNotesWhenPrint}"
              >
                <span class="font-size-14 font-weight-bold toggle-label-width">
                  {{ degreeStore.includeNotesWhenPrint ? 'Yes' : 'No' }}
                </span>
                <v-switch
                  id="degree-note-print-toggle"
                  v-model="notesWhenPrintModel"
                  class="ml-2"
                  color="success"
                  density="compact"
                  hide-details
                />
              </span>
            </label>
          </div>
          <v-btn
            v-if="currentUser.canEditDegreeProgress && !isEditingNote && !noteBody"
            id="create-degree-note-btn"
            class="font-size-16 pl-0"
            color="primary"
            :disabled="degreeStore.disableButtons"
            slim
            text="Create degree note"
            variant="text"
            @click="editNote"
          />
          <div v-if="noteBody && !isEditingNote && (noteUpdatedAt || noteUpdatedBy)" class="font-size-14 pr-2 pb-1">
            <span
              v-if="noteUpdatedBy"
              id="degree-note-updated-by"
              class="text-surface-variant font-weight-normal"
            >
              {{ noteUpdatedBy }}
            </span>
            <span v-if="noteUpdatedAt" class="text-surface-variant">
              {{ noteUpdatedBy ? ' edited this note' : 'Last edited' }}
              <span v-if="isToday(noteUpdatedAt)" id="degree-note-updated-at"> today.</span>
              <span v-if="!isToday(noteUpdatedAt)">
                on <span id="degree-note-updated-at">{{ noteUpdatedAt.toFormat('MMM d, YYYY') }}.</span>
              </span>
            </span>
          </div>
          <div v-if="noteBody && !isEditingNote">
            <div
              id="degree-note-body"
              v-linkified
              class="degree-note-body"
              v-html="noteBody"
            />
            <v-btn
              v-if="currentUser.canEditDegreeProgress"
              id="edit-degree-note-btn"
              class="font-weight-medium pl-0 mb-1 mt-2"
              color="primary"
              :disabled="degreeStore.disableButtons"
              text="Edit degree note"
              variant="text"
              @click="editNote"
            />
          </div>
          <div v-if="isEditingNote">
            <v-textarea
              id="degree-note-input"
              v-model.trim="noteBody"
              aria-labelledby="degree-notes-header"
              auto-grow
              density="compact"
              :disabled="isSaving"
              hide-details
              rows="3"
              variant="outlined"
            />
            <div class="align-center d-flex my-2">
              <ProgressButton
                id="save-degree-note-btn"
                :action="saveNote"
                aria-label="Save Degree Note"
                color="primary"
                :disabled="noteBody === get(degreeStore.degreeNote, 'body') || isSaving"
                :in-progress="isSaving"
                :text="isSaving ? 'Saving...' : 'Save'"
              />
              <v-btn
                id="cancel-degree-note-btn"
                aria-label="Cancel Save Degree Note"
                class="ml-1"
                :disabled="isSaving"
                text="Cancel"
                variant="text"
                @click="cancel"
              />
            </div>
          </div>
        </v-col>
        <v-col
          aria-labelledby="in-progress-courses-header"
          class="d-flex flex-column justify-center"
          cols="12"
          role="region"
          sm="6"
        >
          <div class="align-center d-flex">
            <h3 id="in-progress-courses-header" class="font-size-18 text-medium-emphasis text-no-wrap">In-progress Courses</h3>
            <div v-if="degreeStore.courses.inProgress.length" class="text-no-wrap px-1">
              [<v-btn
                id="show-upper-units-input"
                aria-controls="in-progress-courses"
                :aria-expanded="showInProgressCourses"
                :aria-label="`${showInProgressCourses ? 'Hide' : 'Show'} in-progress courses`"
                class="px-0 text-primary"
                density="compact"
                flat
                size="small"
                style="min-width: 36px !important;"
                :text="showInProgressCourses ? 'hide' : 'show'"
                variant="text"
                @click="() => showInProgressCourses = !showInProgressCourses"
              />]
            </div>
          </div>
          <v-expand-transition v-if="degreeStore.courses.inProgress.length">
            <v-data-table
              v-show="showInProgressCourses"
              id="in-progress-courses"
              borderless
              :cell-props="data => {
                const float = data.column.key === 'units' ? 'float-right' : null
                return {
                  class: `${float} vertical-top`,
                  id: `in-progress-term-${data.item.termId}-section-${data.item.ccn}-column-${data.column.key}`,
                  style: $vuetify.display.mdAndUp ? 'max-width: 200px;' : ''
                }
              }"
              class="no-scrollbar mb-0 w-100"
              density="compact"
              disable-sort
              :headers="[
                {headerProps: {class: 'data-table-column-header text-medium-emphasis'}, key: 'displayName', title: 'Course'},
                {headerProps: {class: 'data-table-column-header text-medium-emphasis float-right'}, key: 'units', title: 'Units'}
              ]"
              hide-default-footer
              hide-default-header
              :items="inProgressCourses"
              primary-key="primaryKey"
              :row-props="data => ({
                id: `tr-in-progress-term-${data.item.termId}-section-${data.item.ccn}`
              })"
            >
              <template #thead="{columns}">
                <caption class="sr-only">In-progress Courses</caption>
                <thead>
                  <tr>
                    <th
                      v-for="(col, index) in columns"
                      :key="index"
                      class="v-data-table__td v-data-table-column--align-start v-data-table__th"
                      :class="col.headerProps.class"
                      colspan="1"
                      rowspan="1"
                    >
                      {{ col.title }}
                    </th>
                  </tr>
                </thead>
              </template>
              <template #item.displayName="{item}">
                <div class="d-flex">
                  <div class="pr-1" :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ item.displayName }}</div>
                  <div
                    v-if="item.enrollmentStatus === 'W'"
                    :id="`in-progress-course-${item.termId}-${item.ccn}-waitlisted`"
                    class="font-size-14 font-weight-bold text-error text-uppercase"
                  >
                    (W<span class="sr-only">aitlisted</span>)
                  </div>
                </div>
              </template>
            </v-data-table>
          </v-expand-transition>
          <span v-if="!degreeStore.courses.inProgress.length" class="text-medium-emphasis font-italic pl-2">None</span>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {DateTime} from 'luxon'
import {getCalnetProfileByUserId} from '@/api/user'
import {mdiCloseThick, mdiOpenInNew, mdiPrinter} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {updateDegreeNote} from '@/api/degree'
import {computed, onMounted, ref, watch} from 'vue'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {each, get, includes} from 'lodash'
import ProgressButton from '@/components/util/ProgressButton.vue'

defineProps({
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()
const degreeStore = useDegreeStore()

const currentUser = contextStore.currentUser
const isEditingNote = ref(false)
const isSaving = ref(false)
const noteBody = ref(undefined)
const noteUpdatedBy = ref(undefined)
const notesWhenPrintModel = ref(degreeStore.includeNotesWhenPrint)
const showInProgressCourses = ref(true)
const showRevisionIndicator = ref(false)
const updatedAtDescription = ref(undefined)

const noteUpdatedAt = computed(() => {
  return degreeStore.degreeNote && DateTime.fromJSDate(new Date(degreeStore.degreeNote.updatedAt))
})

watch(notesWhenPrintModel, () => {
  degreeStore.setIncludeNotesWhenPrint(notesWhenPrintModel.value)
})

const inProgressCourses = computed(() => {
  const courses = []
  each(degreeStore.courses.inProgress, course => {
    courses.push({...course, primaryKey: `${course.termId}-${course.ccn}`})
  })
  return courses
})

onMounted(() => {
  showRevisionIndicator.value = DateTime.fromJSDate(new Date(degreeStore.createdAt)) < DateTime.fromJSDate(new Date(degreeStore.parentTemplateUpdatedAt))
  const updatedAtDate = new Date(degreeStore.updatedAt)
  const isFresh = new Date(degreeStore.createdAt).getTime() === updatedAtDate.getTime()
  const userId = isFresh ? degreeStore.createdBy : degreeStore.updatedBy
  getCalnetProfileByUserId(userId).then(data => {
    const name = data.name || `${data.uid} (UID)`
    updatedAtDescription.value = `${isFresh ? 'Created' : 'Last updated'} by ${name} on ${DateTime.fromJSDate(updatedAtDate).toFormat('MMM d, yyyy')}`
  })
  initNote()
})

const cancel = () => {
  isEditingNote.value = false
  noteBody.value = get(degreeStore.degreeNote, 'body')
  alertScreenReader('Canceled')
  degreeStore.setDisableButtons(false)
  putFocusNextTick(noteBody.value ? 'edit-degree-note-btn' : 'create-degree-note-btn')
}

const editNote = () => {
  degreeStore.setDisableButtons(true)
  isEditingNote.value = true
  putFocusNextTick('degree-note-input')
}

const initNote = () => {
  if (degreeStore.degreeNote) {
    getCalnetProfileByUserId(degreeStore.degreeNote.updatedBy).then(data => {
      noteUpdatedBy.value = data.name || `${data.uid} (UID)`
    })
    noteBody.value = get(degreeStore.degreeNote, 'body')
  }
  isSaving.value = false
}

const isToday = date => {
  return date.hasSame(DateTime.now(),'day')
}

const saveNote = () => {
  isSaving.value = true
  alertScreenReader('Saving')
  updateDegreeNote(degreeStore.templateId, noteBody.value).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      isEditingNote.value = false
      initNote()
      degreeStore.setDisableButtons(false)
      alertScreenReader('Degree note saved')
      putFocusNextTick(noteBody.value ? 'edit-degree-note-btn' : 'create-degree-note-btn')
    })
  })
}
</script>

<style>
.data-table-column-header {
  font-weight: 700 !important;
  height: 30px !important;
}
</style>

<style scoped>
.degree-note-body {
  white-space: pre-line;
}
.toggle-label-width {
  width: 36px;
}
</style>
