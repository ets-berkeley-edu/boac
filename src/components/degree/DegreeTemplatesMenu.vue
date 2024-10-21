<template>
  <div>
    <label
      for="degree-template-select"
      class="font-weight-bold mt-2"
    >Add Degree Check</label>
    <select
      id="degree-template-select"
      v-model="selectedTemplate"
      class="d-block my-2 ml-0 select-menu w-100"
      :disabled="disabled"
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
        :title="template.name"
        :value="template"
      >
        {{ template.name }}
      </option>
    </select>
  </div>
</template>

<script setup>
import {getDegreeTemplates} from '@/api/degree'
import {onMounted, ref, watch} from 'vue'

const props = defineProps({
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

watch(selectedTemplate, props.onSelect)

onMounted(() => getDegreeTemplates().then(data => degreeTemplates.value = data))
</script>
