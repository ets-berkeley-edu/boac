<template>
  <div class="align-center d-flex">
    <label
      id="term-select-label"
      :class="labelClass"
      for="students-term-select"
    >
      <span class="sr-only">Select </span>Term
    </label>
    <div aria-live="polite" class="sr-only">
      Showing enrollments for {{ termNameForSisId(selected) }}.
    </div>
    <select
      id="students-term-select"
      v-model="selected"
      class="select-menu"
      :class="selectClass"
    >
      <option
        v-for="option in options"
        :id="`term-select-option-${option.value}`"
        :key="option.value"
        class="text-no-wrap"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<script setup>
import {map} from 'lodash'
import {nextTick, ref, watch} from 'vue'
import {alertScreenReader} from '@/lib/utils'
import {previousSisTermId, termNameForSisId} from '@/berkeley'
import {useContextStore} from '@/stores/context'

defineProps({
  labelClass: {
    default: 'font-size-16 pr-2 text-medium-emphasis',
    required: false,
    type: String
  },
  selectClass: {
    default: 'students-term-select',
    required: false,
    type: String
  }
})
const nextSisTermId = termId => {
  let nextTermId = ''
  const strTermId = termId.toString()
  switch (strTermId.slice(3)) {
  case '2':
    nextTermId = strTermId.slice(0, 3) + '5'
    break
  case '5':
    nextTermId = strTermId.slice(0, 3) + '8'
    break
  case '8':
    nextTermId = (parseInt(strTermId.slice(0, 3), 10) + 1).toString() + '2'
    break
  default:
    break
  }
  return nextTermId
}

const termOptionForId = termId => {
  const label = termNameForSisId(termId)
  return {
    label: termId === contextStore.config.currentEnrollmentTermId ? `${label} (current)` : label,
    value: termId.toString()
  }
}
const contextStore = useContextStore()
const currentTermId = contextStore.config.currentEnrollmentTermId
const currentUser = contextStore.currentUser
const termIds = [
  nextSisTermId(nextSisTermId(currentTermId)),
  nextSisTermId(currentTermId),
  currentTermId,
  previousSisTermId(currentTermId),
  previousSisTermId(previousSisTermId(currentTermId))
]
const options = ref(map(termIds, termOptionForId))
const selected = ref(termOptionForId(currentUser.preferences.termId).value)

watch(selected, () => {
  if (selected.value !== currentUser.preferences.termId) {
    contextStore.updateCurrentUserPreference('termId', selected.value)
    contextStore.broadcast('termId-user-preference-change', selected.value)
  }
  nextTick(() => {
    alertScreenReader(`${termNameForSisId (selected.value)} selected`)
  })
})
</script>

<style scoped>
.students-term-select {
  min-width: 310px;
}
</style>
