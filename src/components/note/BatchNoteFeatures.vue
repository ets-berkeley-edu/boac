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
      <span v-if="!completeSidSet.length && (addedCohorts.length || addedCuratedGroups.length)" class="font-italic">
        <span
          v-if="addedCohorts.length && !addedCuratedGroups.length"
          id="no-students-per-cohorts-alert"
        >There are no students in the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }}.</span>
        <span
          v-if="addedCuratedGroups.length && !addedCohorts.length"
          id="no-students-per-curated-groups-alert"
        >There are no students in the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }}.</span>
        <span
          v-if="addedCohorts.length && addedCuratedGroups.length"
          id="no-students-alert"
        >
          Neither the {{ pluralize('cohort', addedCohorts.length, {1: ' '}) }} nor the {{ pluralize('group', addedCuratedGroups.length, {1: ' '}) }} have students.
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
        :add-object="addCohortToBatch"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="false"
        :objects="nonAdmitCohorts"
        :remove-object="removeCohortFromBatch"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="nonAdmitCuratedGroups.length"
        :add-object="addCuratedGroupToBatch"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="true"
        :objects="nonAdmitCuratedGroups"
        :remove-object="removeCuratedGroupFromBatch"
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
    addCohortToBatch(cohort) {
      this.setIsRecalculating(true)
      this.addCohort(cohort)
      this.$announcer.polite(`Added cohort '${cohort.name}'`)
    },
    addCuratedGroupToBatch(curatedGroup) {
      this.setIsRecalculating(true)
      this.addCuratedGroup(curatedGroup)
      this.$announcer.polite(`Added ${describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
    },
    removeCohortFromBatch(cohort) {
      this.setIsRecalculating(true)
      this.removeCohort(cohort)
      this.$announcer.polite(`Cohort '${cohort.name}' removed`)
    },
    removeCuratedGroupFromBatch(curatedGroup) {
      this.setIsRecalculating(true)
      this.removeCuratedGroup(curatedGroup)
      this.$announcer.polite(`${this._capitalize(describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}' removed`)
    }
  }
}
</script>
