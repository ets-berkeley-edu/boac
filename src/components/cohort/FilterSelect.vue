<template>
  <div :class="{'border-left-primary': hasLeftBorderStyle}">
    <select
      :id="`filter-select-${type}-${filterRowIndex}`"
      v-model="model"
      :aria-labelledby="labelledby"
      class="bg-white select-menu custom-select"
      :disabled="!options.length"
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
import {each, includes} from 'lodash'

const props = defineProps({
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

const optionGroups = props.hasOptGroups ? {} : undefined

if (props.hasOptGroups) {
  each(props.options, option => {
    if (option.header && !includes(optionGroups, option.header)) {
      optionGroups[option.key] = []
    } else {
      optionGroups[option.group].push(option)
    }
  })
}

const normalizeId = id => {
  return id.toLowerCase().replace(/\W/g, ' ').trim().replace(/ +/g, '-')
}
</script>

<style>
.border-left-primary {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  border-left: 6px solid rgb(var(--v-theme-primary));
}
</style>

<style scoped>
.custom-select {
  -moz-appearance: none;
  -webkit-appearance: none;
  appearance: none;
  border-radius: .25rem;
  border: 1px solid #ced4da;
  color: #495057;
  display: inline-block;
  font-size: 1rem;
  font-weight: 400;
  height: calc(1.5em + .75rem + 2px);
  line-height: 1.5;
  padding: .375rem 1.75rem .375rem .75rem;
  vertical-align: middle;
  width: 100%;
}
.select-menu {
  background-color: #fff;
  height: 44px;
  width: 320px;
}
</style>
