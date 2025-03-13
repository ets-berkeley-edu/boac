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
      v-model="model"
      aria-describedby="find-student-desc"
      aria-label="Name or S I D lookup. Expect auto suggest."
      autocomplete="off"
      base-color="primary"
      class="autocomplete-students autocomplete-with-add-button mt-2"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      clearable
      color="primary"
      :debounce="500"
      density="comfortable"
      :disabled="isStudentSelected"
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
import {each, get, noop, size, trim} from 'lodash'
import {mdiPlus} from '@mdi/js'
import {nextTick, onMounted, onUnmounted, onUpdated, ref, watch} from 'vue'
import type {BasicStudent, BasicStudentLabeled} from '@/lib/types'
import {clearNoteRecipients} from '@/stores/note-edit-session/note-edit-session-utils'
import {findStudentsByNameOrSid} from '@/api/student'
import {getBasicStudent} from '@/api/peer-advising'
import {putFocusNextTick, setComboboxAccessibleLabel} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const findStudentTextInput = ref()
const autocompleteErrorMessage = ref(undefined)
const autoSuggestedStudents = ref<BasicStudentLabeled[]>([])
const contextStore = useContextStore()
const counter = ref(0)
const currentUser = contextStore.currentUser
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isStudentSelected = ref(false)
const isUpdatingAutocomplete = ref(false)
const model = ref<string | undefined>()
const query = ref(undefined)
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

const props = defineProps({
  onSelectStudent: {
    required: true,
    type: Function
  }
})

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
  props.onSelectStudent(undefined)
  clearNoteRecipients()
  vAutocompleteKey.value = new Date().toString()
}

const onUpdateModel = (selectedStudent: BasicStudent) => {
  const sid = get(selectedStudent, 'sid')
  if (sid) {
    isStudentSelected.value = true
    getBasicStudent(sid).then(data => props.onSelectStudent(data))
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
      findStudentsByNameOrSid(search, 20, new AbortController()).then((students: BasicStudent[]) => {
        autoSuggestedStudents.value = []
        each(students, (student: BasicStudent) => {
          autoSuggestedStudents.value.push({
            ...student,
            ...{label: student.label}
          })
        })
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
