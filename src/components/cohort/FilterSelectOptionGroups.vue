<template>
  <div class="secondary-filter">
    <select
      :id="`filter-select-secondary-${filterRowIndex}`"
      v-model="model"
      :aria-labelledby="labelledby"
      class="bg-white select-menu filter-select"
      :disabled="disabled"
    >
      <option :id="`secondary-option-null`" :value="undefined">
        Select...
      </option>
      <optgroup
        v-for="optionGroup in optionGroups"
        :id="normalizeId(`secondary-option-group-${optionGroup.label}`)"
        :key="optionGroup.label"
        :label="optionGroup.label"
      >
        <option
          v-for="option in optionGroup.options"
          :id="normalizeId(`secondary-option-${normalizeId(option.value)}`)"
          :key="option.value"
          :aria-disabled="option.disabled"
          :disabled="option.disabled"
          :value="option"
        >
          {{ option.name }}
        </option>
      </optgroup>
    </select>
  </div>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import type {FilterOptionGroup} from '@/lib/types-cohorts'
import {normalizeId} from '@/lib/utils'

defineProps({
  disabled: {
    required: false,
    type: Boolean
  },
  filterRowIndex: {
    required: true,
    type: [Number, String]
  },
  hasLeftBorderStyle: {
    required: false,
    type: Boolean
  },
  labelledby: {
    required: true,
    type: String
  },
  optionGroups: {
    required: true,
    type: Object as PropType<FilterOptionGroup>
  }
})

// eslint-disable-next-line vue/require-prop-types
const model = defineModel()
</script>

<style scoped>
.border-left-primary select {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
.filter-select {
  height: 44px;
  width: 320px;
}
.secondary-filter {
  padding-left: 6px;
}
</style>
