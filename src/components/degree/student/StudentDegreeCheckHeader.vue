<template>
  <b-container id="student-degree-check-header" class="px-0 mx-0" :fluid="true">
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
              :to="{ path: `/degree/${templateId}/print`, query: { includeNotes: includeNotesWhenPrint }}"
            >
              <font-awesome class="mr-1" icon="print" />
              Print Plan
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
    <b-row class="pt-3">
      <b-col cols="12" sm="4">
        <h3 class="font-size-20 font-weight-bold text-nowrap">Degree Notes</h3>
      </b-col>
      <b-col>
        <div class="align-items-baseline d-flex justify-content-end">
          <div class="pr-3">
            Show notes when printed
          </div>
          <div :class="{'text-success': includeNotesWhenPrint, 'text-danger': !includeNotesWhenPrint}">
            <div class="d-flex">
              <div class="toggle-label">
                {{ includeNotesWhenPrint ? 'Yes' : 'No' }}
              </div>
              <b-form-checkbox id="degree-note-print-toggle" v-model="includeNotesWhenPrint" switch />
            </div>
          </div>
        </div>
      </b-col>
    </b-row>
    <b-row class="pb-2 pt-1">
      <b-col v-if="!isEditingNote" cols="12" md="8">
        <div v-if="!noteBody" id="degree-note-no-data">
          There currently are no degree notes for this student.
        </div>
        <p v-if="noteBody" id="degree-note-body" class="pr-2 degree-note-body">{{ noteBody }}</p>
        <b-btn
          id="create-degree-note-btn"
          class="pl-0"
          :disabled="disableButtons"
          variant="link"
          @click="isEditingNote = true"
        >
          <span v-if="!noteBody">Create new degree notes</span>
          <span v-if="noteBody">Edit degree notes</span>
        </b-btn>
      </b-col>
      <b-col
        v-if="!isEditingNote"
        cols="12"
        md="3"
        offset-md="1"
        class="d-flex justify-content-end"
      >
        <dl class="d-flex flex-row flex-md-column flex-lg-row">
          <div v-if="noteUpdatedBy" class="px-4 pb-3 text-nowrap">
            <dt class="faint-text font-weight-normal">Advisor:</dt>
            <dd id="degree-note-updated-by">{{ noteUpdatedBy }}</dd>
          </div>
          <div v-if="noteUpdatedAt" class="px-4 pb-3 text-nowrap">
            <dt class="faint-text font-weight-normal">Last edited:</dt>
            <dd id="degree-note-updated-at">{{ noteUpdatedAt | moment('MMM D, YYYY') }}</dd>
          </div>
        </dl>
      </b-col>
      <b-col v-if="isEditingNote">
        <b-form-textarea
          id="degree-note-input"
          v-model.trim="noteBody"
          :disabled="isSaving"
          rows="4"
        />
        <div class="d-flex mt-3">
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
              <span v-if="!$_.get(degreeNote, 'body') && !isSaving">Save</span>
              <span v-if="$_.get(degreeNote, 'body') && !isSaving">Edit</span>
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
    includeNotesWhenPrint: false,
    isEditingNote: false,
    isSaving: false,
    noteBody: undefined,
    noteUpdatedBy: undefined,
    updatedAtDescription: undefined
  }),
  computed: {
    noteUpdatedAt() {
      return this.degreeNote && this.$moment(new Date(this.degreeNote.updatedAt))
    }
  },
  created() {
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
    saveNote() {
      this.isSaving = true
      this.updateNote(this.noteBody).then(() => {
        this.isEditingNote = false
        this.initNote()
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
