<template>
  <div>
    <div role="alert">
      <div
        v-if="!isRecalculating && completeSidSet.length"
        id="target-student-count-alert"
        :class="{
          'has-error': mode !== 'editDraft' && completeSidSet.length >= 250,
          'font-weight-bolder': mode !== 'editDraft' && completeSidSet.length >= 500
        }"
        class="font-italic pb-2"
      >
        <span v-if="mode !== 'editDraft'">
          <span v-if="completeSidSet.length < 500">This note will be attached</span>
          <span v-if="completeSidSet.length >= 500">Are you sure you want to attach this note</span>
          to {{ pluralize('student record', completeSidSet.length) }}{{ completeSidSet.length >= 500 ? '?' : '.' }}
        </span>
        <div v-if="!['editTemplate'].includes(mode) && completeSidSet.length > 1">
          <span class="font-weight-700 has-error">Important:</span>
          <span class="text-body">
            {{ mode === 'editDraft' ? 'Updating this draft' : 'Saving as a draft' }} will retain the content of your note
            but not the associated students.
          </span>
        </div>
      </div>
      <span v-if="!completeSidSet.length && (recipients.cohorts.length || recipients.curatedGroups.length)" class="font-italic">
        <span
          v-if="recipients.cohorts.length && !recipients.curatedGroups.length"
          id="no-students-per-cohorts-alert"
        >There are no students in the {{ pluralize('cohort', recipients.cohorts.length, {1: ' '}) }}.</span>
        <span
          v-if="recipients.curatedGroups.length && !recipients.cohorts.length"
          id="no-students-per-curated-groups-alert"
        >There are no students in the {{ pluralize('group', recipients.curatedGroups.length, {1: ' '}) }}.</span>
        <span
          v-if="recipients.cohorts.length && recipients.curatedGroups.length"
          id="no-students-alert"
        >
          Neither the {{ pluralize('cohort', recipients.cohorts.length, {1: ' '}) }}
          nor the {{ pluralize('group', recipients.curatedGroups.length, {1: ' '}) }} have students.
        </span>
      </span>
    </div>
    <div>
      <BatchNoteAddStudent
        :disabled="isSaving || boaSessionExpired"
        dropdown-class="position-relative"
        :on-esc-form-input="cancel"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="nonAdmitCohorts.length"
        :add-object="addCohort"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="false"
        :objects="nonAdmitCohorts"
        :remove-object="removeCohort"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="nonAdmitCuratedGroups.length"
        :add-object="addCuratedGroup"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="true"
        :objects="nonAdmitCuratedGroups"
        :remove-object="removeCuratedGroup"
      />
    </div>
  </div>
</template>

<script>
import BatchNoteAddCohort from '@/components/note/BatchNoteAddCohort'
import BatchNoteAddStudent from '@/components/note/BatchNoteAddStudent'
import Context from '@/mixins/Context'
import NoteEditSession from '@/mixins/NoteEditSession'
import Util from '@/mixins/Util'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'BatchNoteFeatures',
  components: {
    BatchNoteAddCohort,
    BatchNoteAddStudent
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancel: {
      required: true,
      type: Function
    }
  },
  computed: {
    nonAdmitCohorts() {
      return this._reject(this.currentUser.myCohorts, {'domain': 'admitted_students'})
    },
    nonAdmitCuratedGroups() {
      return this._reject(this.currentUser.myCuratedGroups, {'domain': 'admitted_students'})
    }
  },
  methods: {
    addCohort(cohort) {
      this.setRecipients(
        this.recipients.cohorts.concat(cohort),
        this.recipients.curatedGroups,
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Added cohort '${cohort.name}'`)
      })
    },
    addCuratedGroup(curatedGroup) {
      this.setRecipients(
        this.recipients.cohorts,
        this.recipients.curatedGroups.concat(curatedGroup),
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Added ${describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
      })
    },
    removeCohort(cohort) {
      this.setRecipients(
        this._reject(this.recipients.cohorts, ['id', cohort.id]),
        this.recipients.curatedGroups,
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Cohort '${cohort.name}' removed`)
      })
    },
    removeCuratedGroup(curatedGroup) {
      this.setRecipients(
        this.recipients.cohorts,
        this._reject(this.recipients.curatedGroups, ['id', curatedGroup.id]),
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`${this._capitalize(describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}' removed`)
      })
    }
  }
}
</script>
