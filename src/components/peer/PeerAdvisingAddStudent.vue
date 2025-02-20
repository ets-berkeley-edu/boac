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
      autocomplete="off"
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
      :menu-icon="undefined"
      :menu-props="{'contentClass': currentUser.inDemoMode ? 'demo-mode-blur' : ''}"
      type="search"
      validate-on="submit"
      variant="outlined"
      @click:append="onClickAddButton"
      @click:clear="resetAutocomplete"
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
          @click="onClickAddButton"
        />
      </template>
    </v-combobox>
  </div>
</template>

<script setup lang="ts">
import {
  filter, find, get,
  includes,
  map, noop,
  size,
  split,
  trim,
  uniq,
} from 'lodash'
import {mdiPlus} from '@mdi/js'
import type {PropType} from 'vue'
import {nextTick, onUpdated, ref} from 'vue'
import type {BoaUser, StudentSearchResult} from '@/lib/types'
import {createPeerAdvisor} from '@/api/peer-advising.js'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick, setComboboxAccessibleLabel} from '@/lib/utils'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  peerAdvisingDepartmentId: {
    required: true,
    type: Number
  },
  peerAdvisors: {
    required: true,
    type: Array as PropType<BoaUser[]>
  },
  refresh: {
    required: true,
    type: Function
  }
})

const addStudentInput = ref()
const autocompleteErrorMessage = ref(undefined)
const autoSuggestedStudents = ref<StudentSearchResult[]>([])
const error = ref<string | undefined>()
const contextStore = useContextStore()
const currentUser = contextStore.currentUser
const isUpdatingStudentAutocomplete = ref(false)
const query = ref(undefined)
const sidsManuallyAdded = ref<string[]>([])
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

const addStudent = (student: StudentSearchResult) => {
  createPeerAdvisor(props.peerAdvisingDepartmentId, student.uid).then(() => {
    props.refresh()
  }).catch(response => {
    error.value = response
  })
}

const resetAutocomplete = () => {
  autoSuggestedStudents.value = []
  isUpdatingStudentAutocomplete.value = false
  query.value = undefined
  sidsManuallyAdded.value = []
  vAutocompleteKey.value = new Date().toString()
}

const onUpdateModel = (model: StudentSearchResult) => {
  const sid = get(model, 'sid')
  const student: StudentSearchResult | undefined = sid ? find(autoSuggestedStudents.value, ['sid', sid]) : undefined
  if (student) {
    addStudent(student)
  }
}

onUpdated(() => {
  nextTick(() => setComboboxAccessibleLabel(addStudentInput.value.$el, 'Student'))
})

const onClickAddButton = noop

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
        findStudentsByNameOrSid(search, 20, new AbortController()).then((students: StudentSearchResult[]) => {
          const existingPeerAdvisorSids = map(props.peerAdvisors, 'sid')
          students = filter(students, s => !includes(existingPeerAdvisorSids, s.sid))
          autoSuggestedStudents.value = map(students, s => ({label: s.label, sid: s.sid, uid: s.uid}))
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

