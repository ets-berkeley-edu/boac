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
          :aria-label="`${isAddingStudent ? 'Adding' : 'Add'} Peer Advisor to department`"
          class="add-button font-size-16 font-weight-bold"
          :disabled="!student || isAddingStudent"
          :in-progress="isAddingStudent"
          :prepend-icon="isAddingStudent ? undefined : mdiPlusThick"
          :text="isDeletedPeerAdvisor ? 'Restore' : 'Add'"
          @keyup.enter="onClickAddButton"
        />
      </template>
    </AccessibleCombobox>
    <v-expand-transition>
      <div v-if="isDeletedPeerAdvisor" class="ma-3 text-warning">
        <v-icon color="warning" :icon="mdiAlert" /> This student is a deleted Peer Advisor. Click 'Restore' to make them active again.
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup lang="ts">
import type {PropType} from 'vue'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {debounce, filter, find, get, includes, map, size, trim} from 'lodash'
import {mdiAlert, mdiPlusThick} from '@mdi/js'
import type {BasicStudentLabeled, BoaUser} from '@/lib/types'
import AccessibleCombobox from '@/components/util/AccessibleCombobox.vue'
import ProgressButton from '@/components/util/ProgressButton.vue'
import {createPeerAdvisor, restorePeerAdvisor} from '@/api/peer-advising-users.js'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  activeAndDeletedPeerAdvisors: {
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
const isDeletedPeerAdvisor = computed(() => {
  const sid = get(student.value, 'sid')
  return !!sid && map(peerAdvisorsDeleted.value, 'csid').includes(sid)
})
const isFetchingStudents = ref(false)
const peerAdvisorsActive = computed(() => filter(props.activeAndDeletedPeerAdvisors, p => !p.deletedAt) as BoaUser[])
const peerAdvisorsDeleted = computed(() => filter(props.activeAndDeletedPeerAdvisors, p => p.deletedAt) as BoaUser[])
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
    input.removeAttribute('disabled')
  }
  if (student.value) {
    isAddingStudent.value = true
    const done = () => {
      isAddingStudent.value = false
      student.value = undefined
      putFocusNextTick(`${idPrefix}-input`)
    }
    if (isDeletedPeerAdvisor.value) {
      const deletedPeerAdvisor: BoaUser | undefined = find(peerAdvisorsDeleted.value, ['csid', student.value.sid])
      if (deletedPeerAdvisor) {
        restorePeerAdvisor(props.peerAdvisingDepartmentId, deletedPeerAdvisor.id).then(() => {
          props.refresh().finally(done)
        })
      }
    } else {
      createPeerAdvisor(props.peerAdvisingDepartmentId, student.value.uid).then(() => {
        props.refresh().finally(done)
      })
    }
  }
}

const onUpdateSearch = debounce((input: string) => {
  const q = trim(input)
  if (size(q) > 1) {
    isFetchingStudents.value = true
    findStudentsByNameOrSid(q, 20, new AbortController(), true).then(students => {
      const filteredStudents = filter(students, s => !includes(map(peerAdvisorsActive.value, 'csid'), s.sid))
      autoSuggestedStudents.value = map(filteredStudents, s => ({title: s.label, value: s}))
    }).catch(() => putFocusNextTick(`${idPrefix}-input`)
    ).finally(() => isFetchingStudents.value = false)
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
