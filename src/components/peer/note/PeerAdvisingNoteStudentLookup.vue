<template>
  <div class="py-1">
    <label
      for="find-student-input"
      class="font-size-16 font-weight-bold"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span class="font-weight-regular">(name, SID or email)</span>
    </label>
    <AccessibleCombobox
      :key="vAutocompleteKey"
      :id-prefix="idPrefix"
      aria-description="Name or S I D lookup. Expect auto suggest."
      autocomplete="off"
      :clazz="{'demo-mode-blur': currentUser.inDemoMode, 'mt-2': true}"
      :clearable="!isFetchingStudents && !isAddingStudent"
      color="primary"
      density="comfortable"
      :disabled="isSaving"
      :filter-results="onUpdateSearch"
      :get-value="() => get(student, 'label')"
      input-type="search"
      is-autocomplete
      :is-busy="isFetchingStudents"
      :items="autoSuggestedStudents"
      label="Student"
      list-label="Student List"
      :menu-props="{'contentClass': currentUser.inDemoMode ? 'demo-mode-blur' : ''}"
      :on-clear="resetAutocomplete"
      :on-toggle-menu="(isOpen: boolean) => noteStore.setFocusLockDisabled(isOpen)"
      :set-value="selectStudent"
    />
  </div>
</template>

<script setup lang="ts">
import {debounce, get, map, size, trim} from 'lodash'
import {onMounted, onUnmounted, ref} from 'vue'
import {storeToRefs} from 'pinia'
import type {BasicStudentLabeled} from '@/lib/types'
import AccessibleCombobox from '@/components/util/AccessibleCombobox.vue'
import {clearNoteRecipients} from '@/stores/note-edit-session/note-edit-session-utils'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'
import {useNoteStore} from '@/stores/note-edit-session'

const autoSuggestedStudents = ref<{title: string, value: BasicStudentLabeled}[]>([])
const contextStore = useContextStore()
const counter = ref(0)
const currentUser = contextStore.currentUser
const idPrefix = 'find-student-autocomplete'
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isAddingStudent = ref(false)
const isFetchingStudents = ref(false)
const noteStore = useNoteStore()
const {isSaving} = storeToRefs(noteStore)
const query = ref<string | undefined>(undefined)
const student = ref<BasicStudentLabeled>()
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

const props = defineProps({
  onClearSelectedStudent: {
    required: true,
    type: Function
  },
  onSelectStudent: {
    required: true,
    type: Function
  }
})

onMounted(() => {
  return intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100)
})

onUnmounted(() => clearInterval(intervalId.value))

const getInputElement = () => {
  return document.getElementById(`${idPrefix}-input`)
}

const selectStudent = (selected: BasicStudentLabeled) => {
  const input = getInputElement()
  if (input) {
    input.setAttribute('disabled', 'true')
  }
  student.value = selected
  props.onSelectStudent(selected)
}

const onUpdateSearch = debounce((input: string) => {
  const q = trim(input)
  if (size(q) > 1 && !student.value) {
    isFetchingStudents.value = true
    findStudentsByNameOrSid(q, 20, new AbortController(), true).then(students => {
      autoSuggestedStudents.value = map(students, s => ({title: s.label, value: s}))
      isFetchingStudents.value = false
    }).catch(() => putFocusNextTick(`${idPrefix}-input`))
  } else {
    autoSuggestedStudents.value = []
  }
}, 500)

const resetAutocomplete = () => {
  const input = getInputElement()
  if (input) {
    input.setAttribute('disabled', 'false')
  }
  autoSuggestedStudents.value = []
  isFetchingStudents.value = false
  query.value = ''
  student.value = undefined
  props.onClearSelectedStudent()
  clearNoteRecipients()
  vAutocompleteKey.value = new Date().toString()
}
</script>
