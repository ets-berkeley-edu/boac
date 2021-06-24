<template>
  <b-container id="student-degree-check-header" class="px-0 mx-0" :fluid="true">
    <b-row v-if="!$_.includes(dismissedAlerts, templateId) && showRevisionIndicator">
      <b-col>
        <div class="align-items-start d-flex mb-3 p-3 warning-message-container">
          <div class="d-inline-block pr-2 w-100">
            <span class="font-weight-bolder">Note:</span> Revisions to the
            <router-link
              id="original-degree-template"
              target="_blank"
              :to="`/degree/${parentTemplateId}`"
            >
              original degree template <font-awesome icon="external-link-alt" class="pr-1" />
              <span class="sr-only"> (will open new browser tab)</span>
            </router-link>
            have been made since the creation of {{ student.name }}'s degree check. Please update below if necessary.
          </div>
          <div class="align-self-center pr-1">
            <b-btn
              id="dismiss-alert"
              class="p-0"
              size="sm"
              title="Dismiss"
              variant="link"
              @click="dismissAlert(templateId)"
            >
              <font-awesome icon="times" />
              <span class="sr-only">Dismiss alert</span>
            </b-btn>
          </div>
        </div>
      </b-col>
    </b-row>
    <b-row>
      <b-col cols="12" lg="6">
        <h2 class="mb-1 page-section-header">{{ degreeName }}</h2>
        <div class="faint-text font-size-16 font-weight-500 pb-2">
          {{ updatedAtDescription }}
        </div>
      </b-col>
      <b-col cols="12" lg="6">
        <div class="d-flex justify-content-end flex-wrap py-1">
          <div class="pr-2">
            <router-link
              id="print-degree-plan"
              target="_blank"
              :to="`/degree/${templateId}/print?includeNote=${includeNotesWhenPrint}`"
            >
              <font-awesome class="mr-1" icon="print" />
              Print Plan
              <span class="sr-only"> (will open new browser tab)</span>
            </router-link>
          </div>
          <div class="pr-2">
            |
          </div>
          <div class="pr-2">
            <router-link
              id="view-degree-history"
              :to="`/student/${student.uid}/degree/history`"
            >
              View Degree History
            </router-link>
          </div>
          <div v-if="$currentUser.canEditDegreeProgress" class="pr-2">
            |
          </div>
          <div v-if="$currentUser.canEditDegreeProgress" class="pr-2">
            <router-link
              id="create-new-degree"
              :to="`/student/${student.uid}/degree/create`"
            >
              Create New Degree
            </router-link>
          </div>
        </div>
      </b-col>
    </b-row>
    <b-row v-if="isEditingNote || noteBody" class="pl-2 pt-2">
      <b-col cols="12" sm="4">
        <h3 class="font-size-20 font-weight-bold mb-1 text-nowrap">Degree Notes</h3>
        <div v-if="!isEditingNote && (noteUpdatedAt || noteUpdatedBy)" class="d-flex font-size-14">
          <div v-if="noteUpdatedBy" class="pr-2 text-nowrap">
            <span v-if="noteUpdatedBy" class="faint-text font-weight-normal">
              <span id="degree-note-updated-by">{{ noteUpdatedBy }}</span>
            </span>
            <span v-if="noteUpdatedAt" class="faint-text">
              {{ noteUpdatedBy ? 'edited this note' : 'Last edited' }}
              <span v-if="isToday(noteUpdatedAt)"> today.</span>
              <span v-if="!isToday(noteUpdatedAt)">
                on <span id="degree-note-updated-at">{{ noteUpdatedAt | moment('MMM D, YYYY') }}.</span>
              </span>
            </span>
          </div>
        </div>
      </b-col>
      <b-col>
        <div class="align-items-baseline d-flex justify-content-end">
          <label for="degree-note-print-toggle" class="faint-text font-weight-500 pr-3">
            Show notes when printed
          </label>
          <div :class="{'text-success': includeNotesWhenPrint, 'text-danger': !includeNotesWhenPrint}">
            <div class="d-flex">
              <div class="toggle-label">
                {{ includeNotesWhenPrint ? 'Yes' : 'No' }}
              </div>
              <b-form-checkbox
                id="degree-note-print-toggle"
                :checked="includeNotesWhenPrint"
                switch
                @keypress.native.enter="onToggleNotesWhenPrint(!includeNotesWhenPrint)"
                @change="onToggleNotesWhenPrint"
              />
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
    <b-row class="pb-2" :class="{'pt-1': noteBody}">
      <b-col v-if="!isEditingNote" cols="12" md="8">
        <div :class="{'px-2': noteBody, 'pb-2': !$currentUser.canEditDegreeProgress}">
          <div v-if="noteBody" id="degree-note-body" class="degree-note-body">{{ noteBody }}</div>
          <b-btn
            v-if="$currentUser.canEditDegreeProgress"
            id="create-degree-note-btn"
            class="pl-0"
            :disabled="disableButtons"
            variant="link"
            @click="editNote"
          >
            <span v-if="!noteBody">Create degree note</span>
            <span v-if="noteBody">Edit degree note</span>
          </b-btn>
        </div>
      </b-col>
      <b-col v-if="isEditingNote">
        <div class="px-2">
          <b-form-textarea
            id="degree-note-input"
            v-model.trim="noteBody"
            :disabled="isSaving"
            rows="4"
          />
        </div>
        <div class="d-flex ml-2 my-2">
          <div>
            <b-btn
              id="save-degree-note-btn"
              class="btn-primary-color-override"
              :disabled="noteBody === $_.get(degreeNote, 'body') || isSaving"
              variant="primary"
              @click="saveNote"
            >
              <span v-if="isSaving">
                <font-awesome class="mr-1" icon="spinner" spin /> Saving
              </span>
              <span v-if="!isSaving">Save Note</span>
            </b-btn>
          </div>
          <div>
            <b-btn
              id="cancel-degree-note-btn"
              :disabled="isSaving"
              variant="link"
              @click="cancel"
            >
              Cancel
            </b-btn>
          </div>
        </div>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'
import {getCalnetProfileByUserId} from '@/api/user'
import Util from '@/mixins/Util'

export default {
  name: 'StudentDegreeCheckHeader',
  mixins: [DegreeEditSession, Util],
  props: {
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isEditingNote: false,
    isSaving: false,
    noteBody: undefined,
    noteUpdatedBy: undefined,
    showRevisionIndicator: undefined,
    updatedAtDescription: undefined
  }),
  computed: {
    noteUpdatedAt() {
      return this.degreeNote && this.$moment(new Date(this.degreeNote.updatedAt))
    }
  },
  created() {
    this.showRevisionIndicator = this.$moment(new Date(this.createdAt)).isBefore(new Date(this.parentTemplateUpdatedAt))
    const updatedAtDate = new Date(this.updatedAt)
    const isFresh = new Date(this.createdAt) === updatedAtDate
    const userId = isFresh ? this.createdBy : this.updatedBy
    getCalnetProfileByUserId(userId).then(data => {
      const name = data.name || `${data.uid} (UID)`
      this.updatedAtDescription = `${isFresh ? 'Created' : 'Last updated'} by ${name} on ${this.$moment(updatedAtDate).format('MMM D, YYYY')}`
    })
    this.initNote()
  },
  methods: {
    cancel() {
      this.isEditingNote = false
      this.noteBody = this.$_.get(this.degreeNote, 'body')
      this.$announcer.polite('Canceled')
      this.setDisableButtons(false)
      this.$putFocusNextTick('create-degree-note-btn')
    },
    editNote() {
      this.setDisableButtons(true)
      this.isEditingNote = true
      this.$putFocusNextTick('degree-note-input')
      this.$announcer.polite('Enter note in textarea')
    },
    initNote() {
      if (this.degreeNote) {
        getCalnetProfileByUserId(this.degreeNote.updatedBy).then(data => {
          this.noteUpdatedBy = data.name || `${data.uid} (UID)`
        })
        this.noteBody = this.$_.get(this.degreeNote, 'body')
      }
      this.isSaving = false
    },
    onToggleNotesWhenPrint(flag) {
      this.setIncludeNotesWhenPrint(flag)
      this.$announcer.polite(`Note will ${flag ? '' : 'not'} be included in printable page.`)
    },
    saveNote() {
      this.isSaving = true
      this.updateNote(this.noteBody).then(() => {
        this.isEditingNote = false
        this.initNote()
        this.setDisableButtons(false)
        this.$announcer.polite('Note saved')
        this.$putFocusNextTick('create-degree-note-btn')
      })
    }
  }
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
