<template>
  <div>
    <div role="alert">
      <div
        v-if="!isRecalculating && totalRecipientCount"
        id="target-student-count-alert"
        :class="{
          'text-error': mode !== 'editDraft' && totalRecipientCount >= 250,
          'font-weight-bold': mode !== 'editDraft' && totalRecipientCount >= 500
        }"
        class="font-size-14 font-italic pb-2"
      >
        <span v-if="mode !== 'editDraft'">
          <span v-if="totalRecipientCount < 500">This note will be attached</span>
          <span v-if="totalRecipientCount >= 500">Are you sure you want to attach this note</span>
          to {{ pluralize('student record', totalRecipientCount) }}{{ totalRecipientCount >= 500 ? '?' : '.' }}
        </span>
        <div v-if="!['editTemplate'].includes(mode) && totalRecipientCount > 1" class="pt-1">
          <span class="font-weight-bold text-error">Important: </span>
          <span class="text-body">
            {{ mode === 'editDraft' ? 'Updating this draft' : 'Saving as a draft' }} will retain the content of your note
            but not the associated students.
          </span>
        </div>
      </div>
      <span v-if="!totalRecipientCount && (recipients.cohorts.length || recipients.curatedGroups.length)" class="font-italic">
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
        :on-esc-form-input="cancel"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="nonAdmitCohorts.length"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="false"
        :objects="nonAdmitCohorts"
        :remove-object="removeCohort"
        :update="updateCohorts"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="nonAdmitCuratedGroups.length"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="true"
        :objects="nonAdmitCuratedGroups"
        :remove-object="removeCuratedGroup"
        :update="updateCuratedGroups"
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
import {capitalize, differenceBy, findIndex, reject, size} from 'lodash'
import {setNoteRecipients} from '@/stores/note-edit-session/utils'

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
      return reject(this.currentUser.myCohorts, {'domain': 'admitted_students'})
    },
    nonAdmitCuratedGroups() {
      return reject(this.currentUser.myCuratedGroups, {'domain': 'admitted_students'})
    },
    totalRecipientCount() {
      return size(this.completeSidSet)
    }
  },
  methods: {
    updateCohorts(cohorts) {
      const cohort = differenceBy(cohorts, this.recipients.cohorts, 'id')
      if (size(cohorts) > size(this.recipients.cohorts)) {
        setNoteRecipients(
          this.recipients.cohorts.concat(cohort),
          this.recipients.curatedGroups,
          this.recipients.sids
        ).then(() => {
          this.alertScreenReader(`Added cohort '${cohort.name}'`)
        })
      } else {
        this.removeCohort(cohort)
      }
    },
    updateCuratedGroups(curatedGroup) {
      setNoteRecipients(
        this.recipients.cohorts,
        this.recipients.curatedGroups.concat(curatedGroup),
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Added ${describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
      })
    },
    removeCohort(cohort) {
      const index = findIndex(this.recipients.cohorts, {'id': cohort.id})
      this.recipients.cohorts.splice(index, 1)
      setNoteRecipients(
        this.recipients.cohorts,
        this.recipients.curatedGroups,
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Removed cohort '${cohort.name}'`)
      })
    },
    removeCuratedGroup(curatedGroup) {
      const index = findIndex(this.recipients.curatedGroups, {'id': curatedGroup.id})
      this.recipients.curatedGroups.splice(index, 1)
      setNoteRecipients(
        this.recipients.cohorts,
        this.recipients.curatedGroups,
        this.recipients.sids
      ).then(() => {
        this.alertScreenReader(`Removed ${capitalize(describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}'`)
      })
    }
  }
}
</script>
