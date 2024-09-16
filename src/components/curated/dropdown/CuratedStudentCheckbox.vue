<template>
  <div class="checkbox-container" :class="{'checked-checkbox-container': status}">
    <input
      :id="checkboxId"
      v-model="status"
      :aria-label="ariaLabel"
      class="checkbox"
      type="checkbox"
      @update:model-value="toggle"
    />
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {useContextStore} from '@/stores/context'

const props = defineProps({
  domain: {
    required: true,
    type: String
  },
  student: {
    required: true,
    type: Object
  }
})

const contextStore = useContextStore()

const ariaLabel = computed(() => {
  const domainLabel = describeCuratedGroupDomain(props.domain, true)
  return status.value ? `${studentName} selected, ready to add to ${domainLabel}` : `Select ${studentName} to add to ${domainLabel}`
})
const checkboxId = ref(undefined)
const sid = props.student.sid || props.student.csEmplId
const status = ref(false)
const studentName = `${props.student.firstName} ${props.student.lastName}`

onMounted(() => {
  const idFragment = describeCuratedGroupDomain(props.domain, false).replace(' ', '-')
  checkboxId.value = `${props.domain === 'admitted_students' ? 'admit' : 'student'}-${sid}-${idFragment}-checkbox`
  contextStore.setEventHandler('curated-group-select-all', onSelectAll)
  contextStore.setEventHandler('curated-group-deselect-all', onDeselectAll)
})

onUnmounted(() => {
  contextStore.removeEventHandler('curated-group-select-all', onSelectAll)
  contextStore.removeEventHandler('curated-group-deselect-all', onDeselectAll)
})

const onDeselectAll = domain => {
  if (props.domain === domain) {
    status.value = false
  }
}

const onSelectAll = domain => {
  if (props.domain === domain) {
    status.value = true
  }
}

const toggle = checked => {
  const eventName = checked ? 'curated-group-checkbox-checked' : 'curated-group-checkbox-unchecked'
  contextStore.broadcast(eventName, {domain: props.domain, sid})
  alertScreenReader(`${studentName} ${checked ? 'selected' : 'deselected'}`)
}
</script>

<style scoped>
.checkbox {
  height: 18px;
  width: 18px;
}
.checkbox-container {
  height: 28px;
  padding-top: 4px;
  width: 28px;
}
</style>
