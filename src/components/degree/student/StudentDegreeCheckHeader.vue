<template>
  <div>
    <div
      v-if="!includes(degreeStore.dismissedAlerts, degreeStore.templateId) && showRevisionIndicator"
      class="align-center border-b-sm d-flex mb-3 pb-3 pt-4 px-4 warning-message-container"
    >
      <div class="d-inline-block pr-2 w-100">
        <span class="font-weight-700">Note:</span> Revisions to the
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
    <div class="border-b-md border-color-warning mt-4 mx-6">
      <v-container class="py-2 px-0" fluid>
        <v-row>
          <v-col cols="8">
            <h2 class="mb-1 page-section-header">{{ degreeStore.degreeName }}</h2>
            <div class="text-grey-darken-2 font-size-16 font-weight-500 pb-2">
              {{ updatedAtDescription }}
            </div>
          </v-col>
          <v-col cols="4">
            <div class="align-center d-flex flex-wrap justify-end">
              <div class="pr-2">
                <router-link
                  id="print-degree-plan"
                  target="_blank"
                  :to="`/degree/${degreeStore.templateId}/print?includeNote=${degreeStore.includeNotesWhenPrint}`"
                >
                  <v-icon class="mr-1" :icon="mdiPrinter" />
                  Print
                  <span class="sr-only"> (will open new browser tab)</span>
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
      </v-container>
    </div>
    <div class="border-b-md border-color-warning mx-6">
      <v-container class="border-bottom border-warning px-0" fluid>
        <v-row align="start">
          <v-col class="pb-0 pt-1" cols="7">
            <div v-if="isEditingNote || noteBody" class="align-center d-flex justify-space-between">
              <div>
                <h3 class="font-size-20 font-weight-bold text-no-wrap">Degree Notes</h3>
              </div>
              <div class="align-center d-flex justify-content-end">
                <label for="degree-note-print-toggle" class="font-size-14 font-weight-500 pr-2 text-grey-darken-3">
                  Show notes when printed?
                </label>
                <div
                  class="align-center d-flex pr-2"
                  :class="{'text-success': degreeStore.includeNotesWhenPrint, 'text-error': !degreeStore.includeNotesWhenPrint}"
                >
                  <div class="font-size-14 font-weight-bold toggle-label-width">
                    {{ degreeStore.includeNotesWhenPrint ? 'Yes' : 'No' }}
                  </div>
                  <v-switch
                    id="degree-note-print-toggle"
                    v-model="notesWhenPrintModel"
                    color="success"
                    density="compact"
                    hide-details
                  />
                </div>
              </div>
            </div>
            <v-btn
              v-if="currentUser.canEditDegreeProgress && !isEditingNote && !noteBody"
              id="create-degree-note-btn"
              class="font-size-16 pl-0"
              color="primary"
              :disabled="degreeStore.disableButtons"
              text="Create degree note"
              variant="text"
              @click="editNote"
            />
          </v-col>
          <v-col class="py-1" cols="5">
            <h3 class="font-size-20 font-weight-bold pl-2 text-no-wrap">In-progress courses</h3>
          </v-col>
        </v-row>
        <v-row align-v="start">
          <v-col class="py-1" cols="7">
            <div v-if="noteBody && !isEditingNote && (noteUpdatedAt || noteUpdatedBy)" class="font-size-14 pr-2 text-no-wrap">
              <span
                v-if="noteUpdatedBy"
                id="degree-note-updated-by"
                class="text-grey font-weight-normal"
              >
                {{ noteUpdatedBy }}
              </span>
              <span v-if="noteUpdatedAt" class="text-grey">
                {{ noteUpdatedBy ? ' edited this note' : 'Last edited' }}
                <span v-if="isToday(noteUpdatedAt)" id="degree-note-updated-at"> today.</span>
                <span v-if="!isToday(noteUpdatedAt)">
                  on <span id="degree-note-updated-at">{{ noteUpdatedAt.toFormat('MMM D, YYYY') }}.</span>
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
              <div class="mt-2">
                <v-btn
                  v-if="currentUser.canEditDegreeProgress"
                  id="edit-degree-note-btn"
                  class="font-weight-bold pl-0"
                  color="primary"
                  :disabled="degreeStore.disableButtons"
                  text="Edit degree note"
                  variant="text"
                  @click="editNote"
                />
              </div>
            </div>
            <div v-if="isEditingNote">
              <v-textarea
                id="degree-note-input"
                v-model.trim="noteBody"
                density="compact"
                :disabled="isSaving"
                hide-details
                rows="4"
                variant="outlined"
              />
              <div class="d-flex ml-2 my-2">
                <ProgressButton
                  id="save-degree-note-btn"
                  :action="saveNote"
                  color="primary"
                  :disabled="noteBody === get(degreeStore.degreeNote, 'body') || isSaving"
                  :in-progress="isSaving"
                  :text="isSaving ? 'Saving...' : 'Save'"
                />
                <v-btn
                  id="cancel-degree-note-btn"
                  :disabled="isSaving"
                  text="Cancel"
                  variant="text"
                  @click="cancel"
                />
              </div>
            </div>
          </v-col>
          <v-col class="pb-2 pt-1" cols="5">
            <v-data-table
              v-if="degreeStore.courses.inProgress.length"
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
              class="mb-0 w-75"
              density="compact"
              disable-sort
              :headers="[
                {headerProps: {class: 'data-table-column-header'}, key: 'displayName', title: 'Course'},
                {headerProps: {class: 'data-table-column-header float-right'}, key: 'units', title: 'Units'}
              ]"
              hide-default-footer
              :items="inProgressCourses"
              primary-key="primaryKey"
              :row-props="data => ({
                id: `tr-in-progress-term-${data.item.termId}-section-${data.item.ccn}`
              })"
            >
              <template #item.displayName="{item}">
                <div class="d-flex">
                  <div class="pr-1">{{ item.displayName }}</div>
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
            <span v-if="!degreeStore.courses.inProgress.length" class="text-grey">None</span>
          </v-col>
        </v-row>
      </v-container>
    </div>
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
const showRevisionIndicator = ref(undefined)
const updatedAtDescription = ref(undefined)

const noteUpdatedAt = computed(() => {
  return degreeStore.degreeNote && DateTime.fromJSDate(new Date(degreeStore.degreeNote.updatedAt))
})

watch(notesWhenPrintModel, () => {
  degreeStore.setIncludeNotesWhenPrint(notesWhenPrintModel.value)
  alertScreenReader(`Note will ${notesWhenPrintModel.value ? '' : 'not'} be included in printable page.`)
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
    updatedAtDescription.value = `${isFresh ? 'Created' : 'Last updated'} by ${name} on ${DateTime.fromJSDate(updatedAtDate).toFormat('MMM D, yyyy')}`
  })
  initNote()
})

const cancel = () => {
  isEditingNote.value = false
  noteBody.value = get(degreeStore.degreeNote, 'body')
  alertScreenReader('Canceled')
  degreeStore.setDisableButtons(false)
  putFocusNextTick('create-degree-note-btn')
}

const editNote = () => {
  degreeStore.setDisableButtons(true)
  isEditingNote.value = true
  putFocusNextTick('degree-note-input')
  alertScreenReader('Enter note in textarea')
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
  updateDegreeNote(degreeStore.templateId, noteBody.value).then(() => {
    refreshDegreeTemplate(degreeStore.templateId).then(() => {
      isEditingNote.value = false
      initNote()
      degreeStore.setDisableButtons(false)
      alertScreenReader('Note saved')
      putFocusNextTick('create-degree-note-btn')
    })
  })
}
</script>

<style>
.data-table-column-header {
  color: #666;
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
