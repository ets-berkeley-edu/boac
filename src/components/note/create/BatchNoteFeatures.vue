<template>
  <div>
    <div>
      <span aria-live="polite" role="alert">
        <span
          v-if="targetStudentCount"
          id="target-student-count-alert"
          class="font-italic"
          :class="{'has-error': targetStudentCount >= 250, 'font-weight-bolder': targetStudentCount >= 500}">
          Note will be added to {{ 'student record' | pluralize(targetStudentCount) }}.
          <span v-if="targetStudentCount >= 500">Are you sure?</span>
        </span>
        <span v-if="!targetStudentCount && (addedCohorts.length || addedCuratedGroups.length)" class="font-italic">
          <span
            v-if="addedCohorts.length && !addedCuratedGroups.length"
            id="no-students-per-cohorts-alert">There are no students in the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }}.</span>
          <span
            v-if="addedCuratedGroups.length && !addedCohorts.length"
            id="no-students-per-curated-groups-alert">There are no students in the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }}.</span>
          <span
            v-if="addedCohorts.length && addedCuratedGroups.length"
            id="no-students-alert">
            Neither the {{ 'cohort' | pluralize(addedCohorts.length, {1: ' '}) }} nor the {{ 'group' | pluralize(addedCuratedGroups.length, {1: ' '}) }} have students.
          </span>
        </span>
      </span>
    </div>
    <div>
      <BatchNoteAddStudent
        :add-sid="addStudentBySid"
        :disabled="isSaving"
        dropdown-class="position-relative"
        :on-esc-form-input="cancel"
        :remove-sid="removeSid" />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="myCohorts && myCohorts.length"
        :add-object="addCohortToBatch"
        :disabled="isSaving"
        :is-curated-groups-mode="false"
        :objects="myCohorts"
        :remove-object="removeCohortFromBatch" />
    </div>
    <div>
      <BatchNoteAddCohort
        v-if="myCuratedGroups && myCuratedGroups.length"
        :add-object="addCuratedGroupToBatch"
        :disabled="isSaving"
        :is-curated-groups-mode="true"
        :objects="myCuratedGroups"
        :remove-object="removeCuratedGroupFromBatch" />
    </div>
  </div>
</template>

<script>
import BatchNoteAddCohort from '@/components/note/create/BatchNoteAddCohort';
import BatchNoteAddStudent from '@/components/note/create/BatchNoteAddStudent';
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'NoteBatchFeatures',
  components: {
    BatchNoteAddCohort,
    BatchNoteAddStudent
  },
  mixins: [Context, NoteEditSession, UserMetadata, Util],
  props: {
    cancel: Function
  },
  methods: {
    addCohortToBatch(cohort) {
      this.addCohort(cohort);
      this.alertScreenReader(`Added cohort '${cohort.name}'`);
    },
    addCuratedGroupToBatch(curatedGroup) {
      this.addCuratedGroup(curatedGroup);
      this.alertScreenReader(`Added curated group '${curatedGroup.name}'`);
    },
    addStudentBySid(sid) {
      this.addSid(sid);
      this.putFocusNextTick('create-note-add-student-input');
    },
    removeCohortFromBatch(cohort) {
      this.removeCohort(cohort);
      this.alertScreenReader(`Cohort '${cohort.name}' removed`);
    },
    removeCuratedGroupFromBatch(curatedGroup) {
      this.removeCuratedGroup(curatedGroup);
      this.alertScreenReader(`Curated group '${curatedGroup.name}' removed`);
    },
    removeSid(sid) {
      if (this.includes(this.sids, sid)) {
        this.removeStudent(sid);
        this.putFocusNextTick('create-note-add-student-input');
      }
    }
  }
}
</script>
