<template>
  <div class="py-1">
    <label
      for="add-student-input"
      class="font-size-16"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span class="font-weight-regular">(name or SID)</span>
    </label>
    <v-combobox
      id="add-student-input"
      ref="addStudentInput"
      :key="vAutocompleteKey"
      aria-describedby="add-student-desc"
      aria-label="Name or S I D lookup. Expect auto suggest."
      autocomplete="list"
      base-color="primary"
      class="autocomplete-students autocomplete-with-add-button mt-1"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      color="primary"
      density="compact"
      :error-messages="autocompleteErrorMessage"
      :hide-details="!size(autocompleteErrorMessage)"
      :hide-no-data="size(autoSuggestedStudents) < 3"
      item-title="label"
      item-value="sid"
      :items="autoSuggestedStudents"
      :menu-icon="null"
      :menu-props="{
        'content-class': currentUser.inDemoMode ? 'demo-mode-blur' : ''
      }"
      type="search"
      validate-on="submit"
      variant="outlined"
      @click:append="onClickAddButton"
      @click:clear="resetAutocomplete"
      @keydown.esc="onEscFormInput"
      @update:menu="isOpen => noteStore.setFocusLockDisabled(isOpen)"
      @update:search="onUpdateSearch"
      @update:model-value="onUpdateModel"
    >
      <template #append>
        <v-btn
          id="add-student-add-button"
          aria-label="Add Student to Note"
          class="add-button add-button-height"
          color="primary"
          :disabled="!size(query) && !size(sidsManuallyAdded)"
          :prepend-icon="mdiPlus"
          text="Add"
          variant="flat"
          @click.stop="onClickAddButton"
        />
      </template>
    </v-combobox>
  </div>
</template>

<script setup>
import {
  differenceWith,
  each,
  filter,
  find,
  includes,
  isEqual,
  join,
  map,
  remove,
  size,
  split,
  trim,
  uniq
} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {nextTick, onMounted, onUpdated, ref} from 'vue'
import {findStudentsByNameOrSid, getStudentsBySids} from '@/api/student'
import {alertScreenReader, putFocusNextTick, setComboboxAccessibleLabel} from '@/lib/utils'
import {setNoteRecipient, setNoteRecipients} from '@/stores/note-edit-session/note-edit-session-utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

defineProps({
  onEscFormInput: {
    default: () => {},
    required: false,
    type: Function
  }
})

const contextStore = useContextStore()
const noteStore = useNoteStore()

const addStudentInput = ref()
const autocompleteErrorMessage = ref(undefined)
const addedStudents = ref([])
const autoSuggestedStudents = ref([])
const currentUser = contextStore.currentUser
const isUpdatingStudentAutocomplete = ref(false)
const query = ref(undefined)
const sidsManuallyAdded = ref([])
const vAutocompleteKey = ref(new Date())

onMounted(() => {
  const sids = noteStore.recipients.sids
  if (sids.length) {
    getStudentsBySids(sids).then(students => {
      addedStudents.value = students
    })
  }
})

const addStudent = student => {
  addedStudents.value.push(student)
  setNoteRecipient(student.sid).then(() => {
    alertScreenReader(`Added ${student.label} to batch note`)
    putFocusNextTick('add-student-input')
    resetAutocomplete()
  })
}

const resetAutocomplete = () => {
  autoSuggestedStudents.value = []
  isUpdatingStudentAutocomplete.value = false
  query.value = undefined
  sidsManuallyAdded.value = []
  vAutocompleteKey.value = new Date()
}

const onUpdateModel = sid => {
  const student = sid ? find(autoSuggestedStudents.value, ['sid', sid.sid]) : null
  if (student && !noteStore.recipients.sids.includes(student.sid)) {
    addStudent(student)
  }
}

onUpdated(() => {
  nextTick(() => setComboboxAccessibleLabel(addStudentInput.value.$el, 'Student'))
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
        putFocusNextTick('add-student-input')
      })
    })
  } else {
    resetAutocomplete()
    return Promise.resolve()
  }
}
const onUpdateSearch = input => {
  query.value = input
  autocompleteErrorMessage.value = undefined
  autoSuggestedStudents.value = []
  input = trim(input, ' ,\n\t')
  if (input.length) {
    sidsManuallyAdded.value = /^[0-9,\s]*$/.test(input) ? uniq(split(input, /[ ,]+/)) : []
    if (sidsManuallyAdded.value.length <= 1) {
      const search = input.replace((/\s+|\r\n|\n|\r/gm),' ')
      isUpdatingStudentAutocomplete.value = true
      if (size(search) > 1) {
        findStudentsByNameOrSid(search, 20, new AbortController()).then(students => {
          const existingSids = map(addedStudents.value, 'sid')
          students = filter(students, s => !includes(existingSids, s.sid))
          autoSuggestedStudents.value = map(students, s => ({label: s.label, sid: s.sid}))
          isUpdatingStudentAutocomplete.value = false
        }).catch(() => putFocusNextTick('add-student-input'))
      }
    }
  }
}
</script>

<style scoped>
.add-button-height {
  height: 40px;
}
.autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
</style>

