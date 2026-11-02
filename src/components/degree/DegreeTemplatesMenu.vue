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
      autocomplete="off"
      :disabled="disabled"
    >
      <option
        aria-label="choose degree check"
        class="font-weight-black"
        :selected="selectedTemplate === undefined"
        :value="undefined"
      >
        Choose...
      </option>
      <option
        v-for="template in unarchivedDegreeTemplates"
        :id="`degree-template-option-${template.id}`"
        :key="template.id"
        :aria-label="`Add degree check ${template.name}`"
        class="wrap-anywhere"
        :title="template.name"
        :value="template"
      >
        {{ template.name }}
      </option>
      <option
        v-if="archivedDegreeTemplates.length"
        aria-hidden="true"
        disabled
      />
      <optgroup
        v-if="archivedDegreeTemplates.length"
        id="degree-template-archived-optgroup"
        label="Archived Degree Checks"
      >
        <option
          v-for="template in archivedDegreeTemplates"
          :id="`degree-template-option-${template.id}`"
          :key="template.id"
          :aria-label="`Add archived degree check ${template.name}`"
          class="wrap-anywhere"
          :title="template.name"
          :value="template"
        >
          {{ template.name }}
        </option>
      </optgroup>
    </select>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {filter as _filter, sortBy} from 'lodash'
import {getDegreeTemplates} from '@/api/degree'

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

const archivedDegreeTemplates = computed(() => sortBy(_filter(degreeTemplates.value, 'archivedAt'), 'name'))
const unarchivedDegreeTemplates = computed(() => sortBy(_filter(degreeTemplates.value, t => !t.archivedAt), 'name'))

watch(selectedTemplate, props.onSelect)

onMounted(() => getDegreeTemplates().then(data => degreeTemplates.value = data))
</script>
