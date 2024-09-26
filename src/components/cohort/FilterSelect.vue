<template>
  <div :class="{'border-left-primary': hasLeftBorderStyle, 'secondary-filter': !hasLeftBorderStyle}">
    <select
      :id="`filter-select-${type}-${filterRowIndex}`"
      v-model="model"
      :aria-labelledby="labelledby"
      class="bg-white select-menu filter-select"
      :disabled="disabled"
    >
      <option :id="`${type}-option-null`" :value="undefined">
        Select...
      </option>
      <template v-if="hasOptGroups">
        <optgroup
          v-for="(groupOptions, label) in optionGroups"
          :id="normalizeId(`${type}-option-group-${label}`)"
          :key="label"
          :label="label"
        >
          <option
            v-for="option in groupOptions"
            :id="normalizeId(`${type}-option-${option.value}`)"
            :key="option.key"
            :aria-disabled="option.disabled"
            :disabled="option.disabled"
            :value="option"
          >
            {{ option.name }}
          </option>
        </optgroup>
      </template>
      <template v-if="!hasOptGroups">
        <option
          v-for="option in options"
          :id="normalizeId(`${type}-option-${option.value}`)"
          :key="option.key"
          :aria-disabled="option.disabled"
          :disabled="option.disabled"
          :value="option"
        >
          {{ option.name || option.label.primary }}
        </option>
      </template>
    </select>
  </div>
</template>

<script setup>
import {computed} from 'vue'
import {each, includes} from 'lodash'
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
  hasLeftBorderStyle: {
    required: false,
    type: Boolean
  },
  hasOptGroups: {
    required: false,
    type: Boolean
  },
  labelledby: {
    required: true,
    type: String
  },
  options: {
    default: () => [],
    required: false,
    type: [Object, Array]
  },
  type: {
    required: true,
    type: String,
    validator: s => ['primary', 'secondary'].indexOf(s) > -1
  }
})

// eslint-disable-next-line vue/require-prop-types
const model = defineModel()

const optionGroups = computed(() => {
  const value = props.hasOptGroups ? {} : undefined
  if (props.hasOptGroups) {
    each(props.options, option => {
      if (option.header && !includes(value, option.header)) {
        value[option.key] = []
      } else {
        value[option.group].push(option)
      }
    })
  }
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
.secondary-filter {
  padding-left: 6px;
}
</style>
