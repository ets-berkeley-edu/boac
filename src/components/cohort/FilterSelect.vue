<template>
  <div class="secondary-filter">
    <select
      :id="`filter-select-secondary-${filterRowIndex}`"
      v-model="model"
      :aria-labelledby="labelledby"
      class="bg-white select-menu filter-select"
      autocomplete="off"
      :disabled="disabled"
    >
      <option :id="`secondary-option-null`" :value="undefined">
        Select...
      </option>
      <option
        v-for="option in options"
        :id="normalizeId(`secondary-option-${option.value}`)"
        :key="option.key"
        :aria-disabled="option.disabled"
        :disabled="option.disabled"
        :value="option"
      >
        {{ option.name || option.label.primary }}
      </option>
    </select>
  </div>
</template>

<script lang="ts" setup>
import type {PropType} from 'vue'
import type {FilterOption} from '@/lib/types-cohorts'
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
  labelledby: {
    required: true,
    type: String
  },
  options: {
    required: true,
    type: Array as PropType<FilterOption[]>
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
