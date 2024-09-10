<template>
  <div>
    <div
      v-if="totalRecipientCount || recipients.cohorts.length || recipients.curatedGroups.length"
      aria-live="polite"
      role="alert"
    >
      <transition
        id="target-student-count-alert"
        :class="{
          'text-error': noteStore.mode !== 'editDraft' && totalRecipientCount >= 250,
          'font-weight-bold': noteStore.mode !== 'editDraft' && totalRecipientCount >= 500
        }"
        class="font-size-14 font-italic pb-2"
        name="alert"
      >
        <div v-if="!noteStore.isRecalculating && totalRecipientCount">
          <span v-if="noteStore.mode !== 'editDraft'">
            <span v-if="totalRecipientCount < 500">This note will be attached</span>
            <span v-if="totalRecipientCount >= 500">Are you sure you want to attach this note</span>
            to {{ pluralize('student record', totalRecipientCount) }}{{ totalRecipientCount >= 500 ? '?' : '.' }}
          </span>
          <div v-if="!['editTemplate'].includes(noteStore.mode) && totalRecipientCount > 1" class="pt-1">
            <span class="font-weight-bold text-error">Important: </span>
            <span class="text-body">
              {{ noteStore.mode === 'editDraft' ? 'Updating this draft' : 'Saving as a draft' }} will retain the content of your note
              but not the associated students.
            </span>
          </div>
        </div>
      </transition>
      <div class="mt-1">
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
    </div>
    <div class="mt-1">
      <BatchNoteAddStudent :on-esc-form-input="discard" />
    </div>
    <div class="mt-2">
      <BatchNoteAddCohort
        v-if="size(nonAdmitCohorts)"
        :add="addCohort"
        :is-curated-groups-mode="false"
        :options="nonAdmitCohorts"
        :remove="removeCohort"
        :selected-options="recipients.cohorts"
      />
    </div>
    <div class="mt-2">
      <BatchNoteAddCohort
        v-if="size(nonAdmitCuratedGroups)"
        :add="addCuratedGroup"
        :is-curated-groups-mode="true"
        :options="nonAdmitCuratedGroups"
        :remove="removeCuratedGroup"
        :selected-options="recipients.curatedGroups"
      />
    </div>
  </div>
</template>

<script setup>
import BatchNoteAddCohort from '@/components/note/BatchNoteAddCohort'
import BatchNoteAddStudent from '@/components/note/BatchNoteAddStudent'
import {alertScreenReader, pluralize} from '@/lib/utils'
import {capitalize, findIndex, reject, size} from 'lodash'
import {computed} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {setNoteRecipients} from '@/stores/note-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

defineProps({
  discard: {
    required: true,
    type: Function
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()
const recipients = computed(() => noteStore.recipients)

const nonAdmitCohorts = computed(() => {
  return reject(contextStore.currentUser.myCohorts, {'domain': 'admitted_students'})
})
const nonAdmitCuratedGroups = computed(() => {
  return reject(contextStore.currentUser.myCuratedGroups, {'domain': 'admitted_students'})
})
const totalRecipientCount = computed(() => {
  return size(noteStore.completeSidSet)
})

const removeCohort = cohort => {
  const index = findIndex(recipients.value.cohorts, {'id': cohort.id})
  recipients.value.cohorts.splice(index, 1)
  setNoteRecipients(
    recipients.value.cohorts,
    recipients.value.curatedGroups,
    recipients.value.sids
  ).then(() => {
    alertScreenReader(`Removed cohort '${cohort.name}'`)
  })
}

const removeCuratedGroup = curatedGroup => {
  const index = findIndex(recipients.value.curatedGroups, {'id': curatedGroup.id})
  recipients.value.curatedGroups.splice(index, 1)
  setNoteRecipients(
    recipients.value.cohorts,
    recipients.value.curatedGroups,
    recipients.value.sids
  ).then(() => {
    alertScreenReader(`Removed ${capitalize(describeCuratedGroupDomain(curatedGroup.domain))} '${curatedGroup.name}'`)
  })
}

const addCohort = cohort => {
  setNoteRecipients(
    recipients.value.cohorts.concat([cohort]),
    recipients.value.curatedGroups,
    recipients.value.sids
  ).then(() => {
    alertScreenReader(`Added cohort '${cohort.name}'`)
  })
}

const addCuratedGroup = curatedGroup => {
  setNoteRecipients(
    recipients.value.cohorts,
    recipients.value.curatedGroups.concat([curatedGroup]),
    recipients.value.sids
  ).then(() => {
    alertScreenReader(`Added ${describeCuratedGroupDomain(curatedGroup.domain)} '${curatedGroup.name}'`)
  })
}
</script>

<!-- The CSS 'alert' classes below are used by the 'transition' block above. -->
<style scoped>
.alert-enter-active,
.alert-leave-active {
  transition: opacity 0.5s ease;
}
.alert-enter-from,
.alert-leave-to {
  opacity: 0;
}
</style>
