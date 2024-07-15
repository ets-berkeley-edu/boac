<template>
  <div>
    <label
      for="create-note-add-student-input"
      class="font-size-16 font-weight-700"
    >
      Student
    </label>
    <div id="create-note-add-student-desc" class="font-size-14 pb-2">
      Type a name, individual Student Identification (SID), or paste a list of SID numbers below.
      (Example: 9999999990, 9999999991)
    </div>
    <div class="align-center d-flex">
      <v-autocomplete
        id="create-note-add-student"
        :key="vAutocompleteKey"
        aria-describedby="create-note-add-student-desc"
        auto-select-first
        autocomplete="off"
        class="autocomplete-students autocomplete-with-add-button"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        density="comfortable"
        :disabled="noteStore.isSaving || noteStore.boaSessionExpired"
        :error-messages="autocompleteErrorMessage"
        :hide-details="!size(autocompleteErrorMessage)"
        :hide-no-data="size(autoSuggestedStudents) < 3"
        item-title="label"
        item-value="sid"
        :items="autoSuggestedStudents"
        :menu-icon="null"
        type="search"
        variant="outlined"
        @click:append="onClickAddButton"
        @click:clear="resetAutocomplete"
        @keydown.esc="onEscFormInput"
        @update:search="onUpdateSearch"
        @update:model-value="onUpdateModel"
      >
        <template #append>
          <v-btn
            id="create-note-add-student-add-button"
            class="add-button"
            color="primary"
            :prepend-icon="mdiPlus"
            text="Add"
            variant="flat"
            @click.stop="onClickAddButton"
          />
        </template>
      </v-autocomplete>
    </div>
    <div v-for="(addedStudent, index) in addedStudents" :key="addedStudent.sid" class="mt-2">
      <v-chip
        :id="`batch-note-student-${index}`"
        class="v-chip-content-override font-weight-bold text-medium-emphasis text-uppercase text-no-wrap truncate-with-ellipsis"
        :class="{'demo-mode-blur': useContextStore().currentUser.inDemoMode}"
        closable
        :close-label="`Remove ${addedStudent.label} from batch note`"
        density="comfortable"
        variant="outlined"
        @click:close="removeStudent(addedStudent)"
        @keyup.enter="removeStudent(addedStudent)"
      >
        <span class="truncate-with-ellipsis">{{ addedStudent.label }}</span>
        <template #close>
          <v-icon color="error" :icon="mdiCloseCircle" />
        </template>
      </v-chip>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {
  differenceWith,
  each,
  filter,
  find,
  findIndex,
  includes, isEqual,
  join,
  map,
  remove,
  size,
  split,
  trim,
  uniq,
  without
} from 'lodash'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'
import {mdiCloseCircle, mdiPlus} from '@mdi/js'
import {setNoteRecipient, setNoteRecipients} from '@/stores/note-edit-session/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'
import {onMounted, ref} from 'vue'

defineProps({
  onEscFormInput: {
    default: () => {},
    required: false,
    type: Function
  }
})

const noteStore = useNoteStore()

const autocompleteErrorMessage = ref(undefined)
const addedStudents = ref([])
const autoSuggestedStudents = ref([])
const isUpdatingStudentAutocomplete = ref(false)
const query = ref(undefined)
const sidsManuallyAdded = ref([])
const vAutocompleteKey = ref(new Date())

const resetAutocomplete = () => {
  autoSuggestedStudents.value = []
  isUpdatingStudentAutocomplete.value = false
  query.value = undefined
  sidsManuallyAdded.value = []
  vAutocompleteKey.value = new Date()
}

const onUpdateModel = sid => {
  const student = sid ? find(autoSuggestedStudents.value, ['sid', sid]) : null
  if (student && !noteStore.recipients.sids.includes(student.sid)) {
    noteStore.setIsRecalculating(true)
    addedStudents.value.push(student)
    setNoteRecipient(sid).then(() => {
      alertScreenReader(`${student.label} added to batch note`)
      resetAutocomplete()
    })
  } else {
    resetAutocomplete()
  }
}

onMounted(() => {
  const sids = noteStore.recipients.sids
  if (sids.length) {
    getStudentsBySids(sids).then(students => each(students, s => onUpdateModel(s.sid)))
  }
})

const onClickAddButton = () => {
  const sids = sidsManuallyAdded.value
  if (sids.length) {
    return getStudentsBySids(sids).then(data => {
      noteStore.setIsRecalculating(true)
      const sidsToAdd = []
      each(data, student => {
        addedStudents.value.push(student)
        sidsToAdd.push(student.sid)
        remove(sids, s => s === student.sid)
      })
      const recipients = noteStore.recipients
      setNoteRecipients(
        recipients.cohorts,
        recipients.curatedGroups,
        uniq(recipients.sids.concat(sidsToAdd))
      ).then(() => {
        alertScreenReader(`${sidsToAdd.length} students added to batch note`)
        const sidsNotFound = differenceWith(sids, sidsToAdd, isEqual)
        if (sidsNotFound.length) {
          const suffix = sidsNotFound.length === 1 ? '' : 's'
          autocompleteErrorMessage.value = `No student${suffix} found with SID${suffix} ${join(sidsNotFound)}.`
        }
        resetAutocomplete()
        putFocusNextTick('create-note-add-student-input')
      })
    })
  } else {
    resetAutocomplete()
    return Promise.resolve()
  }
}

const onUpdateSearch = input => {
  autocompleteErrorMessage.value = undefined
  input = trim(input, ' ,\n\t')
  if (input.length) {
    sidsManuallyAdded.value = /^[0-9,\s]*$/.test(input) ? uniq(split(input, /\s+|,+,/)) : []
    if (!sidsManuallyAdded.value.length) {
      query.value = input.replace((/\s+|\r\n|\n|\r/gm),' ')
      isUpdatingStudentAutocomplete.value = true
      if (size(query.value) > 1) {
        findStudentsByNameOrSid(query.value, 20).then(students => {
          const existingSids = map(addedStudents.value, 'sid')
          students = filter(students, s => !includes(existingSids, s.sid))
          autoSuggestedStudents.value = map(students, s => ({label: s.label, sid: s.sid}))
          isUpdatingStudentAutocomplete.value = false
        })
      }
    }
  }
}

const removeStudent = student => {
  if (student) {
    const index = findIndex(addedStudents.value, {'sid': student.sid})
    addedStudents.value.splice(index, 1)
    const recipients = noteStore.recipients
    if (recipients.sids.includes(student.sid)) {
      setNoteRecipients(
        recipients.cohorts,
        recipients.curatedGroups,
        without(recipients.sids, student.sid)
      ).then(() => {
        putFocusNextTick('create-note-add-student-input')
      })
    }
    alertScreenReader(`${student.label} removed from batch note`)
  }
}
</script>

<style>
.v-input__append:has(button) {
  margin-left: 0 !important;
}
</style>

<style scoped>
.add-button {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  height: 48px !important;
}
.autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
</style>

