<template>
  <div class="border-left-primary">
    <select
      :id="`filter-select-primary-${filterRowIndex}`"
      v-model="model"
      :aria-labelledBy="labelledBy"
      class="bg-white select-menu filter-select"
      :disabled="disabled"
    >
      <option :id="`primary-option-null`" :value="undefined">
        Select...
      </option>
      <optgroup
        v-for="(options, label) in optionGroups"
        :id="normalizeId(`primary-option-group-${label}`)"
        :key="label"
        :label="label"
      >
        <option
          v-for="option in options"
          :id="normalizeId(`primary-option-${option.value}`)"
          :key="option.key"
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
import {computed} from 'vue'
import {each, includes} from 'lodash'
import type {FilterCategory} from '@/lib/types-cohorts'
import {normalizeId} from '@/lib/utils'

const props = defineProps({
  disabled: {
    required: false,
    type: Boolean
  },
  filterRowIndex: {
    required: true,
    type: [Number, String]
  },
  labelledBy: {
    required: true,
    type: String
  },
  filterCategories: {
    required: true,
    type: Array as PropType<FilterCategory[]>
  }
})

const model = defineModel<string>()

// TODO: The types and computed values below will be removed when the structure of props.filterCategories is modified.
export type OptionGroups = {
  [label: string | number]: Option[];
}

export type Option = {
  key: string,
  disabled?: boolean,
  name: string,
  value: string
}

const optionGroups = computed<OptionGroups>(() => {
  const value = {}
  each(props.filterCategories, option => {
    if (option.header && !includes(value, option.header)) {
      value[option.key] = []
    } else {
      value[option.group].push(option)
    }
  })
  return value
})
</script>

<style scoped>
.border-left-primary {
  border-left: 6px solid rgb(var(--v-theme-primary));
}
.border-left-primary select {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
}
.filter-select {
  height: 44px;
  width: 320px;
}
</style>
