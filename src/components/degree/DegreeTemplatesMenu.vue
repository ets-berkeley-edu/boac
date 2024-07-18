<template>
  <div>
    <div class="mb-2">
      <label
        for="degree-template-select"
        class="font-weight-700 input-label mt-2"
      >Add Degree Check</label>
    </div>
    <select
      id="degree-template-select"
      v-model="selectedTemplate"
      class="bordered-select d-block mb-2 ml-0 select-menu w-100"
      :disabled="disabled"
      @change="() => onSelect(selectedTemplate)"
    >
      <option
        class="font-weight-black"
        :selected="selectedTemplate === undefined"
        :value="undefined"
      >
        Choose<span class="sr-only">&nbsp;degree check</span>...
      </option>
      <option
        v-for="template in degreeTemplates"
        :id="`degree-template-option-${template.id}`"
        :key="template.id"
        :aria-label="`Add degree check ${template.name}`"
        class="truncate-with-ellipsis"
        :selected="get(selectedTemplate, 'id') === template.id"
        :value="template"
      >
        {{ template.name }}
      </option>
    </select>
  </div>
</template>

<script setup>
import {getDegreeTemplates} from '@/api/degree'
import {get} from 'lodash'
import {onMounted, ref} from 'vue'

defineProps({
  onSelect: {
    required: true,
    type: Function
  },
  disabled: {
    required: false,
    type: Boolean
  }
})

const degreeTemplates = ref(undefined)
const selectedTemplate = ref(undefined)

onMounted(() => {
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
  })
})
</script>

<style scoped>
.bordered-select {
  border: 1px solid #000;
}
</style>
