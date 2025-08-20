<template>
  <div class="py-1">
    <label
      for="find-student-autocomplete-input"
      class="font-size-16 font-weight-bold"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span class="font-weight-regular">(name, SID or email)</span>
    </label>
    <div v-if="loadingStatus === 'prefill'" class="mt-4 d-flex align-center">
      <v-progress-circular
        indeterminate
        size="18"
        width="2"
        class="mr-2"
      />
      <span>Loading student…</span>
    </div>
    <AccessibleCombobox
      v-else
      :key="vAutocompleteKey"
      :id-prefix="idPrefix"
      aria-description="Name, S I D, or email lookup. Expect auto suggest."
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
import {nextTick, onMounted, onUnmounted, ref} from 'vue'
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
const loadingStatus = ref<'ready' | 'prefill'>('ready')

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
  // Prefill from recipients if a student was preselected (e.g., via + New Note button)
  const preselectedSid = noteStore.recipients?.sids?.[0]
  if (preselectedSid && !student.value) {
    loadingStatus.value = 'prefill'
    isFetchingStudents.value = true
    findStudentsByNameOrSid(preselectedSid, 1, new AbortController(), true)
      .then(results => {
        const s = results && results[0]
        if (s) {
          // Set the combobox's model so the value shows up
          student.value = s
          // Mirror the "selected" behavior by disabling the input
          const input = getInputElement()
          if (input) {
            input.setAttribute('disabled', 'true')
          }
          return nextTick().then(() => selectStudent(s))
        }
      })
      .then(() => {
        loadingStatus.value = 'ready'
        isFetchingStudents.value = false
      })
  }

  // existing ticker
  return (intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100))
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
    input.removeAttribute('disabled')
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
