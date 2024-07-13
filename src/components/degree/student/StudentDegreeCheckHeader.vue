<template>
  <div>
    <v-container class="border-bottom border-warning my-2 mx-0 px-0" fluid>
      <v-row v-if="!includes(degreeStore.dismissedAlerts, degreeStore.templateId) && showRevisionIndicator">
        <v-col>
          <div class="align-items-start d-flex mb-3 p-3 warning-message-container">
            <div class="d-inline-block pr-2 w-100">
              <span class="font-weight-700">Note:</span> Revisions to the
              <router-link
                id="original-degree-template"
                target="_blank"
                :to="`/degree/${degreeStore.parentTemplateId}`"
              >
                original degree template <v-icon :icon="mdiOpenInNew" class="pr-1" />
                <span class="sr-only"> (will open new browser tab)</span>
              </router-link>
              have been made since the creation of <span :class="{'demo-mode-blur': currentUser.inDemoMode}">{{ student.name }}'s</span>
              degree check. Please update below if necessary.
            </div>
            <div class="align-self-center pr-1">
              <v-btn
                id="dismiss-alert"
                class="p-0"
                size="sm"
                title="Dismiss"
                variant="text"
                @click="degreeStore.dismissAlert(templateId)"
              >
                <v-icon :icon="mdiClose" />
                <span class="sr-only">Dismiss alert</span>
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="8">
          <h2 class="mb-1 page-section-header">{{ degreeStore.degreeName }}</h2>
          <div class="text-grey font-size-16 font-weight-500 pb-2">
            {{ updatedAtDescription }}
          </div>
        </v-col>
        <v-col cols="4">
          <div class="d-flex flex-wrap py-1">
            <div class="pr-2">
              <router-link
                id="print-degree-plan"
                target="_blank"
                :to="`/degree/${degreeStore.templateId}/print?includeNote=${degreeStore.includeNotesWhenPrint}`"
              >
                <v-icon class="mr-1" :icon="mdiPrinterOutline" />
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
    <v-container class="border-bottom border-warning my-2 mx-0 px-0" fluid>
      <v-row align-v="start">
        <v-col cols="8">
          <div v-if="isEditingNote || noteBody" class="d-flex justify-space-between">
            <div>
              <h3 class="font-size-20 font-weight-bold text-no-wrap">Degree Notes</h3>
            </div>
            <div class="align-items-baseline d-flex justify-content-end">
              <label for="degree-note-print-toggle" class="text-grey font-weight-500 pr-3">
                Show notes when printed
              </label>
              <div :class="{'text-success': includeNotesWhenPrint, 'text-danger': !includeNotesWhenPrint}">
                <div class="d-flex">
                  <div class="toggle-label">
                    {{ degreeStore.includeNotesWhenPrint ? 'Yes' : 'No' }}
                  </div>
                  <v-switch
                    id="degree-note-print-toggle"
                    :checked="degreeStore.includeNotesWhenPrint"
                    density="compact"
                    color="primary"
                    hide-details
                    switch
                    @keydown.enter="onToggleNotesWhenPrint(!degreeStore.includeNotesWhenPrint)"
                    @change="onToggleNotesWhenPrint"
                  />
                </div>
              </div>
            </div>
          </div>
          <v-btn
            v-if="currentUser.canEditDegreeProgress && !isEditingNote && !noteBody"
            id="create-degree-note-btn"
            class="pl-0 pt-0"
            :disabled="degreeStore.disableButtons"
            variant="text"
            @click="editNote"
          >
            Create degree note
          </v-btn>
        </v-col>
        <v-col cols="4">
          <h3 class="font-size-20 font-weight-bold mb-1 text-no-wrap">In-progress courses</h3>
        </v-col>
      </v-row>
      <v-row align-v="start">
        <v-col cols="8">
          <div v-if="noteBody && !isEditingNote && (noteUpdatedAt || noteUpdatedBy)" class="d-flex font-size-14">
            <div v-if="noteUpdatedBy" class="pr-2 text-no-wrap">
              <span v-if="noteUpdatedBy" class="text-grey font-weight-normal">
                <span id="degree-note-updated-by">{{ noteUpdatedBy }}</span>
              </span>
              <span v-if="noteUpdatedAt" class="text-grey">
                {{ noteUpdatedBy ? 'edited this note' : 'Last edited' }}
                <span v-if="isToday(noteUpdatedAt)"> today.</span>
                <span v-if="!isToday(noteUpdatedAt)">
                  on <span id="degree-note-updated-at">{{ noteUpdatedAt.toFormat('MMM D, YYYY') }}.</span>
                </span>
              </span>
            </div>
          </div>
          <div>
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
                class="pl-0"
                :disabled="disableButtons"
                text="Edit degree note"
                variant="text"
                @click="editNote"
              />
            </div>
            <div v-if="isEditingNote">
              <div class="px-2">
                <v-textarea
                  id="degree-note-input"
                  v-model.trim="noteBody"
                  variant="outlined"
                  clearable
                  :disabled="isSaving"
                  rows="4"
                />
              </div>
            </div>
            <div>
              <div class="d-flex ml-2 my-2">
                <div>
                  <v-btn
                    id="save-degree-note-btn"
                    class="btn-primary-color-override"
                    color="primary"
                    :disabled="noteBody === get(degreeStore.degreeNote, 'body') || isSaving"
                    @click="saveNote"
                  >
                    <span v-if="isSaving">
                      <v-progress-circular class="mr-1" size="small" />
                    </span>
                    <span v-if="!isSaving">Save Note</span>
                  </v-btn>
                </div>
                <div>
                  <v-btn
                    id="cancel-degree-note-btn"
                    :disabled="isSaving"
                    text="Cancel"
                    variant="text"
                    @click="cancel"
                  />
                </div>
              </div>
            </div>
          </div>
        </v-col>
        <v-col class="pb-2" cols="4">
          <!--
            TODO:
            * `class` needs to move out of headers
            * tbody-class
            * thead-class
          -->
          <v-data-table
            v-if="degreeStore.courses.inProgress.length"
            id="in-progress-courses"
            borderless
            class="mb-0"
            :headers="[
              {key: 'displayName', title: 'Course'},
              {class: 'float-right', key: 'units', title: 'Units'}
            ]"
            :items="getInProgressCourses"
            primary-key="primaryKey"
            density="compact"
            tbody-class="font-size-14"
            thead-class="border-bottom font-size-14"
          >
            <template #item.displayName="{item}">
              <div class="d-flex">
                <div class="pr-1">{{ item.displayName }}</div>
                <div
                  v-if="item.enrollmentStatus === 'W'"
                  :id="`in-progress-course-${item.termId}-${item.sectionId}-waitlisted`"
                  class="font-size-14 error font-weight-bold text-uppercase"
                >
                  (W<span class="sr-only">aitlisted</span>)
                </div>
              </div>
            </template>
          </v-data-table>
          <span v-if="!degreeStore.courses.inProgress.length" class="text-grey pl-1">None</span>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick, studentRoutePath} from '@/lib/utils'
import {DateTime} from 'luxon'
import {getCalnetProfileByUserId} from '@/api/user'
import {mdiClose, mdiOpenInNew, mdiPrinterOutline} from '@mdi/js'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {updateDegreeNote} from '@/api/degree'
import {computed, onMounted, ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {each, get} from 'lodash'

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
const showRevisionIndicator = ref(undefined)
const updatedAtDescription = ref(undefined)

const noteUpdatedAt = computed(() => {
  return degreeStore.degreeNote && DateTime.fromJSDate(new Date(degreeStore.degreeNote.updatedAt))
})

onMounted(() => {
  showRevisionIndicator.value = DateTime.fromJSDate(new Date(degreeStore.createdAt)) < DateTime.fromJSDate(new Date(degreeStore.parentTemplateUpdatedAt))
  const updatedAtDate = new Date(degreeStore.updatedAt)
  const isFresh = new Date(degreeStore.createdAt) === updatedAtDate
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

const getInProgressCourses = () => {
  const courses = []
  each(degreeStore.courses.inProgress, course => {
    courses.push({...course, primaryKey: `${course.termId}-${course.ccn}`})
  })
  return courses
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

const onToggleNotesWhenPrint = flag => {
  degreeStore.setIncludeNotesWhenPrint(flag)
  alertScreenReader(`Note will ${flag ? '' : 'not'} be included in printable page.`)
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

<style scoped>
.degree-note-body {
  white-space: pre-line;
}
.toggle-label {
  font-size: 14px;
  font-weight: bolder;
  padding: 2px 8px 0 0;
  width: 30px;
}
</style>
