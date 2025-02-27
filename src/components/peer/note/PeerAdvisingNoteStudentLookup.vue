<template>
  <div class="py-1">
    <label
      for="find-student-input"
      class="font-size-16 font-weight-bold"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span class="font-weight-regular">(name, SID or email)</span>
    </label>
    <v-combobox
      id="find-student-autocomplete"
      ref="findStudentTextInput"
      :key="vAutocompleteKey"
      v-model="comboboxModel"
      aria-describedby="find-student-desc"
      aria-label="Name or S I D lookup. Expect auto suggest."
      autocomplete="off"
      base-color="primary"
      class="autocomplete-students autocomplete-with-add-button mt-2"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      clearable
      color="primary"
      density="comfortable"
      :error-messages="autocompleteErrorMessage"
      :hide-details="!size(autocompleteErrorMessage)"
      :hide-no-data="size(autoSuggestedStudents) < 3"
      item-title="label"
      item-value="sid"
      :items="autoSuggestedStudents"
      :menu-icon="undefined"
      :menu-props="{'contentClass': currentUser.inDemoMode ? 'demo-mode-blur' : ''}"
      persistent-clear
      type="search"
      validate-on="submit"
      variant="outlined"
      @click:clear="resetAutocomplete"
      @update:search="onUpdateSearch"
      @update:model-value="onUpdateModel"
    >
      <template #append>
        <v-btn
          id="find-student-add-button"
          aria-label="Add Student to Note"
          class="add-button add-button-height"
          color="primary"
          :disabled="!size(query) || isUpdatingAutocomplete || !!size(autoSuggestedStudents)"
          :prepend-icon="mdiPlus"
          text="Add"
          variant="flat"
          @click="onClickAddButton"
        />
      </template>
    </v-combobox>
  </div>
</template>

<script setup lang="ts">
import {find, get, map, noop, size, trim} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {nextTick, onMounted, onUnmounted, onUpdated, ref, watch} from 'vue'
import type {StudentSearchResult} from '@/lib/types'
import {clearNoteRecipients, setNoteRecipient} from '@/stores/note-edit-session/note-edit-session-utils'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick, setComboboxAccessibleLabel} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const findStudentTextInput = ref()
const autocompleteErrorMessage = ref(undefined)
const autoSuggestedStudents = ref<StudentSearchResult[]>([])
const comboboxModel = ref()
const contextStore = useContextStore()
const counter = ref(0)
const currentUser = contextStore.currentUser
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isUpdatingAutocomplete = ref(false)
const query = ref(undefined)
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

watch(query, value => {
  if (!trim(value)) {
    resetAutocomplete()
  }
})

onMounted(() => {
  return intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100)
})

onUnmounted(() => clearInterval(intervalId.value))

const resetAutocomplete = () => {
  autoSuggestedStudents.value = []
  isUpdatingAutocomplete.value = false
  query.value = undefined
  clearNoteRecipients()
  vAutocompleteKey.value = new Date().toString()
}

const onUpdateModel = (model: StudentSearchResult) => {
  const sid = get(model, 'sid')
  const student: StudentSearchResult | undefined = sid ? find(autoSuggestedStudents.value, ['sid', sid]) : undefined
  if (student) {
    setNoteRecipient(student.sid)
  }
}

onUpdated(() => {
  nextTick(() => setComboboxAccessibleLabel(findStudentTextInput.value.$el, 'Student'))
})

const onClickAddButton = noop

const onUpdateSearch = input => {
  query.value = input
  autocompleteErrorMessage.value = undefined
  autoSuggestedStudents.value = []
  input = trim(input, ' ,\n\t')
  if (input.length) {
    const search = input.replace((/\s+|\r\n|\n|\r/gm),' ')
    isUpdatingAutocomplete.value = true
    if (size(search) > 1) {
      findStudentsByNameOrSid(search, 20, new AbortController()).then((students: StudentSearchResult[]) => {
        autoSuggestedStudents.value = map(students, s => ({label: s.label, sid: s.sid, uid: s.uid}))
        isUpdatingAutocomplete.value = false
      }).catch(() => putFocusNextTick('find-student-input'))
    }
  }
}
</script>

<style scoped>
.add-button-height {
  height: 48px;
}
.autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
</style>
