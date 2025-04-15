<template>
  <div class="py-1">
    <label
      :for="`${idPrefix}-input`"
      class="font-size-16 font-weight-bold"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span aria-hidden="true" class="font-weight-regular">(name, email or SID)</span>
      <span class="sr-only">Student (name, email or S I D)</span>
    </label>
    <AccessibleCombobox
      :key="vAutocompleteKey"
      :id-prefix="idPrefix"
      aria-description="Name or S I D lookup. Expect auto suggest."
      autocomplete="off"
      :clazz="{'demo-mode-blur': currentUser.inDemoMode, 'autocomplete-students autocomplete-with-add-button mt-2': true}"
      :clearable="!isFetchingStudents && !isAddingStudent"
      color="primary"
      density="compact"
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
      :set-value="selectStudent"
    >
      <template #append>
        <ProgressButton
          :id="`${idPrefix}-add-button`"
          :action="onClickAddButton"
          :aria-label="`${isAddingStudent ? 'Adding' : 'Add'} Student to Note`"
          class="add-button font-size-16 font-weight-bold"
          :disabled="!student || isAddingStudent"
          :in-progress="isAddingStudent"
          :prepend-icon="isAddingStudent ? undefined : mdiPlusThick"
          text="Add"
        />
      </template>
    </AccessibleCombobox>
  </div>
</template>

<script setup lang="ts">
import {debounce, filter, get, includes, map, size, trim} from 'lodash'
import type {PropType} from 'vue'
import {mdiPlusThick} from '@mdi/js'
import {onMounted, onUnmounted, ref} from 'vue'
import type {BasicStudentLabeled, BoaUser} from '@/lib/types'
import AccessibleCombobox from '@/components/util/AccessibleCombobox.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {createPeerAdvisor} from '@/api/peer-advising-users.js'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  excludeTheseStudents: {
    required: true,
    type: Array as PropType<BoaUser[]>
  },
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
  refresh: {
    required: true,
    type: Function
  }
})

const autoSuggestedStudents = ref<{title: string, value: BasicStudentLabeled}[]>([])
const contextStore = useContextStore()
const counter = ref(0)
const currentUser = contextStore.currentUser
const idPrefix = 'add-peer-advisor'
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isAddingStudent = ref(false)
const isFetchingStudents = ref(false)
const query = ref<string | undefined>()
const student = ref<BasicStudentLabeled>()
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

onMounted(() => {
  return intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100)
})

onUnmounted(() => clearInterval(intervalId.value))

const getInputElement = () => {
  return document.getElementById(`${idPrefix}-input`)
}

const onClickAddButton = () => {
  const input = getInputElement()
  if (input) {
    input.setAttribute('disabled', 'false')
  }
  if (student.value) {
    isAddingStudent.value = true
    const done = () => {
      isAddingStudent.value = false
      student.value = undefined
    }
    createPeerAdvisor(props.peerAdvisingDepartmentId, student.value.uid).then(() => {
      props.refresh().then(done)
    })
  }
}

const onUpdateSearch = debounce((input: string) => {
  const q = trim(input)
  if (size(q) > 1) {
    isFetchingStudents.value = true
    findStudentsByNameOrSid(q, 20, new AbortController(), true).then(students => {
      const existingPeerAdvisorSids = map(props.excludeTheseStudents, 'sid')
      const filteredStudents = filter(students, s => !includes(existingPeerAdvisorSids, s.sid))
      autoSuggestedStudents.value = map(filteredStudents, s => ({title: s.label, value: s}))
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
  vAutocompleteKey.value = new Date().toString()
}

const selectStudent = (selected: BasicStudentLabeled) => {
  const input = getInputElement()
  if (input) {
    input.setAttribute('disabled', 'true')
  }
  student.value = selected
  putFocusNextTick(`${idPrefix}-add-button`)
}
</script>

<style scoped>
.add-button {
  height: 40px;
}
/* eslint-disable-next-line vue-scoped-css/no-unused-selector */
.autocomplete-students {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
</style>
