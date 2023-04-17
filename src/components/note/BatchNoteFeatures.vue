<template>
  <div>
    <div>
      <span role="alert">
        <transition name="drawer">
          <div
            v-if="!isRecalculating && completeSidSet.length"
            id="target-student-count-alert"
            :class="{'has-error': completeSidSet.length >= 250, 'font-weight-bolder': completeSidSet.length >= 500}"
            class="font-italic pb-2"
          >
            <span v-if="completeSidSet.length < 500">This note will be attached</span>
            <span v-if="completeSidSet.length >= 500">Are you sure you want to attach this note</span>
            to {{ pluralize('student record', completeSidSet.length) }}.
            <div v-if="completeSidSet.length > 1">
              <span class="font-weight-700 has-error">Important:</span> Saving as a draft will save the content of your
              note but not the associated students.
            </div>
          </div>
        </transition>
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
      </span>
    </div>
    <div>
      <BatchNoteAddStudent
        :add-sid="addStudentBySid"
        :add-sid-list="addStudentsBySidList"
        :disabled="isSaving || boaSessionExpired"
        :on-esc-form-input="cancel"
        :remove-sid="removeSid"
        dropdown-class="position-relative"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="$currentUser.myCohorts.length"
        :add-object="addCohortToBatch"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="false"
        :objects="$currentUser.myCohorts"
        :remove-object="removeCohortFromBatch"
      />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="$currentUser.myCuratedGroups.length"
        :add-object="addCuratedGroupToBatch"
        :disabled="isSaving || boaSessionExpired"
        :is-curated-groups-mode="true"
        :objects="$_.filter($currentUser.myCuratedGroups, ['domain', 'default'])"
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

export default {
  name: 'BatchNoteFeatures',
  components: {
    BatchNoteAddCohort,
    BatchNoteAddStudent
  },
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancel: Function
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
      this.$announcer.polite(`Added ${this.describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
    },
    addStudentBySid(sid) {
      this.setIsRecalculating(true)
      this.addSid(sid)
      this.$putFocusNextTick('create-note-add-student-input')
    },
    addStudentsBySidList(sidList) {
      this.setIsRecalculating(true)
      this.addSidList(sidList)
      this.$putFocusNextTick('create-note-add-student-input')
    },
    removeCohortFromBatch(cohort) {
      this.setIsRecalculating(true)
      this.removeCohort(cohort)
      this.$announcer.polite(`Cohort '${cohort.name}' removed`)
    },
    removeCuratedGroupFromBatch(curatedGroup) {
      this.setIsRecalculating(true)
      this.removeCuratedGroup(curatedGroup)
      this.$announcer.polite(`${this.$_.capitalize(this.describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}' removed`)
    },
    removeSid(sid) {
      if (this.$_.includes(this.sids, sid)) {
        this.setIsRecalculating(true)
        this.removeStudent(sid)
        this.$putFocusNextTick('create-note-add-student-input')
      }
    }
  }
}
</script>
