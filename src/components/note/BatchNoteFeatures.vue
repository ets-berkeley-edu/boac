<template>
  <div>
    <div v-if="totalRecipientCount || useNoteStore().recipients.cohorts.length || useNoteStore().recipients.curatedGroups.length" role="alert">
      <div
        v-if="!useNoteStore().isRecalculating && totalRecipientCount"
        id="target-student-count-alert"
        :class="{
          'text-error': useNoteStore().mode !== 'editDraft' && totalRecipientCount >= 250,
          'font-weight-bold': useNoteStore().mode !== 'editDraft' && totalRecipientCount >= 500
        }"
        class="font-size-14 font-italic pb-2"
      >
        <span v-if="useNoteStore().mode !== 'editDraft'">
          <span v-if="totalRecipientCount < 500">This note will be attached</span>
          <span v-if="totalRecipientCount >= 500">Are you sure you want to attach this note</span>
          to {{ pluralize('student record', totalRecipientCount) }}{{ totalRecipientCount >= 500 ? '?' : '.' }}
        </span>
        <div v-if="!['editTemplate'].includes(useNoteStore().mode) && totalRecipientCount > 1" class="pt-1">
          <span class="font-weight-bold text-error">Important: </span>
          <span class="text-body">
            {{ useNoteStore().mode === 'editDraft' ? 'Updating this draft' : 'Saving as a draft' }} will retain the content of your note
            but not the associated students.
          </span>
        </div>
      </div>
      <span v-if="!totalRecipientCount && (useNoteStore().recipients.cohorts.length || useNoteStore().recipients.curatedGroups.length)" class="font-italic">
        <span
          v-if="useNoteStore().recipients.cohorts.length && !useNoteStore().recipients.curatedGroups.length"
          id="no-students-per-cohorts-alert"
        >There are no students in the {{ pluralize('cohort', useNoteStore().recipients.cohorts.length, {1: ' '}) }}.</span>
        <span
          v-if="useNoteStore().recipients.curatedGroups.length && !useNoteStore().recipients.cohorts.length"
          id="no-students-per-curated-groups-alert"
        >There are no students in the {{ pluralize('group', useNoteStore().recipients.curatedGroups.length, {1: ' '}) }}.</span>
        <span
          v-if="useNoteStore().recipients.cohorts.length && useNoteStore().recipients.curatedGroups.length"
          id="no-students-alert"
        >
          Neither the {{ pluralize('cohort', useNoteStore().recipients.cohorts.length, {1: ' '}) }}
          nor the {{ pluralize('group', useNoteStore().recipients.curatedGroups.length, {1: ' '}) }} have students.
        </span>
      </span>
    </div>
    <BatchNoteAddStudent :on-esc-form-input="discard" />
    <BatchNoteAddCohort
      v-if="size(nonAdmitCohorts)"
      :is-curated-groups-mode="false"
      :objects="nonAdmitCohorts"
      :remove-object="removeCohort"
      :update="updateCohorts"
    />
    <BatchNoteAddCohort
      v-if="size(nonAdmitCuratedGroups)"
      :is-curated-groups-mode="true"
      :objects="nonAdmitCuratedGroups"
      :remove-object="removeCuratedGroup"
      :update="updateCuratedGroups"
    />
  </div>
</template>

<script>
import BatchNoteAddCohort from '@/components/note/BatchNoteAddCohort'
import BatchNoteAddStudent from '@/components/note/BatchNoteAddStudent'
import {alertScreenReader, pluralize} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {capitalize, differenceBy, findIndex, reject, size} from 'lodash'
import {setNoteRecipients} from '@/stores/note-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

export default {
  name: 'BatchNoteFeatures',
  components: {
    BatchNoteAddCohort,
    BatchNoteAddStudent
  },
  props: {
    discard: {
      required: true,
      type: Function
    }
  },
  computed: {
    nonAdmitCohorts() {
      return reject(useContextStore().currentUser.myCohorts, {'domain': 'admitted_students'})
    },
    nonAdmitCuratedGroups() {
      return reject(useContextStore().currentUser.myCuratedGroups, {'domain': 'admitted_students'})
    },
    totalRecipientCount() {
      return size(useNoteStore().completeSidSet)
    }
  },
  methods: {
    pluralize,
    removeCohort(cohort) {
      const index = findIndex(useNoteStore().recipients.cohorts, {'id': cohort.id})
      useNoteStore().recipients.cohorts.splice(index, 1)
      setNoteRecipients(
        useNoteStore().recipients.cohorts,
        useNoteStore().recipients.curatedGroups,
        useNoteStore().recipients.sids
      ).then(() => {
        alertScreenReader(`Removed cohort '${cohort.name}'`)
      })
    },
    removeCuratedGroup(curatedGroup) {
      const index = findIndex(useNoteStore().recipients.curatedGroups, {'id': curatedGroup.id})
      useNoteStore().recipients.curatedGroups.splice(index, 1)
      setNoteRecipients(
        useNoteStore().recipients.cohorts,
        useNoteStore().recipients.curatedGroups,
        useNoteStore().recipients.sids
      ).then(() => {
        alertScreenReader(`Removed ${capitalize(describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}'`)
      })
    },
    size,
    updateCohorts(cohorts) {
      const cohort = differenceBy(cohorts, useNoteStore().recipients.cohorts, 'id')
      if (size(cohorts) > size(useNoteStore().recipients.cohorts)) {
        setNoteRecipients(
          useNoteStore().recipients.cohorts.concat(cohort),
          useNoteStore().recipients.curatedGroups,
          useNoteStore().recipients.sids
        ).then(() => {
          alertScreenReader(`Added cohort '${cohort.name}'`)
        })
      } else {
        this.removeCohort(cohort)
      }
    },
    updateCuratedGroups(curatedGroups) {
      const curatedGroup = differenceBy(curatedGroups, useNoteStore().recipients.curatedGroups, 'id')
      if (size(curatedGroups) > size(useNoteStore().recipients.curatedGroups)) {
        setNoteRecipients(
          useNoteStore().recipients.cohorts,
          useNoteStore().recipients.curatedGroups.concat(curatedGroup),
          useNoteStore().recipients.sids
        ).then(() => {
          alertScreenReader(`Added ${describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
        })
      } else {
        this.removeCuratedGroup(curatedGroup)
      }
    },
    useNoteStore
  }
}
</script>
