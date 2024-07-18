<template>
  <div>
    <div>
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
    >
      <option
        v-if="isNil(selectedTemplate)"
        class="font-weight-black"
        selected
        :value="undefined"
      >
        Choose<span class="sr-only">&nbsp;degree check</span>...
      </option>
      <option
        v-if="!isNil(selectedTemplate)"
        class="truncate-with-ellipsis"
        selected
        :value="selectedTemplate"
      >
        {{ selectedTemplate.name }}
      </option>
      <option
        v-for="template in degreeTemplates"
        :id="`degree-template-option-${template.id}`"
        :key="template.id"
        :aria-label="`Add degree check ${template.name}`"
        class="truncate-with-ellipsis"
        @click="select(template)"
      >
        {{ template.name }}
      </option>
    </select>
  </div>
</template>

<script setup>
import {getDegreeTemplates} from '@/api/degree'
import {isNil} from 'lodash'
import {onMounted, ref} from 'vue'

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

onMounted(() => {
  getDegreeTemplates().then(data => {
    degreeTemplates.value = data
  })
})

const select = template => {
  selectedTemplate.value = template
  props.onSelect(template)
}
</script>

<style scoped>
.bordered-select {
  border: 1px solid #000;
}
</style>
