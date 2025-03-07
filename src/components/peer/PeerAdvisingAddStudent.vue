<template>
  <div class="py-1">
    <label
      for="add-student-input"
      class="font-size-16 font-weight-bold"
    >
      <span class="mr-2 text-weight-bold">Student</span>
      <span class="font-weight-regular">(name or SID)</span>
    </label>
    <v-combobox
      id="add-student-input"
      ref="addStudentInput"
      :key="vAutocompleteKey"
      v-model="comboboxModel"
      aria-describedby="add-student-desc"
      aria-label="Name or S I D lookup. Expect auto suggest."
      autocomplete="off"
      base-color="primary"
      class="autocomplete-students autocomplete-with-add-button mt-2"
      :class="{'demo-mode-blur': currentUser.inDemoMode}"
      color="primary"
      density="compact"
      :disabled="isAddingStudent"
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
        <v-progress-circular
          v-if="isAddingStudent"
          :model-value="counter"
          :indeterminate="true"
          :size="36"
          :width="7"
          :color="['primary', 'warning', 'success'][Math.round(counter / 10) % 3]"
        />
        <v-btn
          v-if="!isAddingStudent"
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
import type {PropType} from 'vue'
import {mdiPlus} from '@mdi/js'
import {nextTick, onMounted, onUnmounted, onUpdated, ref} from 'vue'
import type {BasicStudent, BoaUser} from '@/lib/types'
import {createPeerAdvisor} from '@/api/peer-advising.js'
import {findStudentsByNameOrSid} from '@/api/student'
import {putFocusNextTick, setComboboxAccessibleLabel} from '@/lib/utils'
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

const addStudentInput = ref()
const autocompleteErrorMessage = ref(undefined)
const autoSuggestedStudents = ref<BasicStudent[]>([])
const comboboxModel = ref()
const contextStore = useContextStore()
const counter = ref(0)
const currentUser = contextStore.currentUser
const error = ref<string | undefined>()
const intervalId = ref<ReturnType<typeof setTimeout>>()
const isAddingStudent = ref(false)
const isUpdatingStudentAutocomplete = ref(false)
const query = ref(undefined)
const sidsManuallyAdded = ref<string[]>([])
const vAutocompleteKey = ref<PropertyKey>(new Date().toString())

onMounted(() => {
  return intervalId.value = setInterval(() => {
    counter.value = counter.value === 100 ? 0 : counter.value + 1
  }, 100)
})

onUnmounted(() => clearInterval(intervalId.value))

const resetAutocomplete = () => {
  autoSuggestedStudents.value = []
  isUpdatingStudentAutocomplete.value = false
  query.value = undefined
  sidsManuallyAdded.value = []
  vAutocompleteKey.value = new Date().toString()
}

const onUpdateModel = (model: BasicStudent) => {
  const sid = get(model, 'sid')
  const student: BasicStudent | undefined = sid ? find(autoSuggestedStudents.value, ['sid', sid]) : undefined
  if (student) {
    isAddingStudent.value = true
    const done = () => {
      comboboxModel.value = undefined
      isAddingStudent.value = false
    }
    createPeerAdvisor(props.peerAdvisingDepartmentId, student.uid).then(() => {
      props.refresh().then(done)
    }).catch(response => {
      error.value = response
      done()
    })
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
        findStudentsByNameOrSid(search, 20, new AbortController()).then((students: BasicStudent[]) => {
          const existingPeerAdvisorSids = map(props.excludeTheseStudents, 'sid')
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

