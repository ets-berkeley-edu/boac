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
        v-for="filterCategory in filterCategories"
        :id="normalizeId(`primary-option-group-${normalizeId(filterCategory['label'])}`)"
        :key="filterCategory['label']"
        :label="filterCategory['label']"
      >
        <option
          v-for="option in filterCategory['options']"
          :id="normalizeId(`primary-option-${normalizeId(option.key)}`)"
          :key="option.key"
          :aria-disabled="option.disabled"
          :disabled="option.disabled"
          :value="option"
        >
          {{ option.label.primary }}
        </option>
      </optgroup>
    </select>
  </div>
</template>

<script lang="ts" setup>
import {cloneDeep} from 'lodash'
import type {FilterOptionGroup} from '@/lib/types-cohorts'
import {normalizeId} from '@/lib/utils'
import {useCohortStore} from '@/stores/cohort-edit-session'

defineProps({
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
  }
})

const model = defineModel<object>()

const filterCategories: FilterOptionGroup = cloneDeep(useCohortStore().filterCategories)
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
