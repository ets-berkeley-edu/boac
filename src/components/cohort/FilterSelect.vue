<template>
  <pre v-if="optionGroups && false">
    {{ options }}
  </pre>
  <div :class="{'border-left-primary': hasLeftBorderStyle}">
    <select
      :id="`filter-select-${type}-${filterRowIndex}`"
      v-model="vModelProxy"
      class="bg-white select-menu custom-select"
      :aria-labelledby="labelledby"
      :disabled="!options.length"
    >
      <option :id="`${type}-option-null`" :value="undefined">
        Select...
      </option>
      <template v-if="hasOptGroups">
        <option value="1">HAS OPT GROUPS</option>
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
            class="h-100 min-height-unset py-1 pl-8"
            :disabled="option.disabled"
            :value="option"
          >
            {{ option.name }}
          </option>
        </optgroup>
      </template>
      <template v-if="!hasOptGroups">
        <option value="1">NO OPT GROUPS</option>
        <option
          v-for="option in options"
          :id="normalizeId(`${type}-option-${option.value}`)"
          :key="option.key"
          :aria-disabled="option.disabled"
          class="h-100 min-height-unset py-1 pl-8"
          :disabled="option.disabled"
          :value="option"
        >
          {{ getLabel(option) }}
        </option>
      </template>
    </select>
  </div>
</template>

<script>
import {each, includes} from 'lodash'

export default {
  name: 'FilterSelect',
  props: {
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
    },
    setModelObject: {
      required: true,
      type: Function
    },
    vModelObject: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    optionGroups: undefined
  }),
  computed: {
    vModelProxy: {
      get() {
        return this.vModelObject
      },
      set(value) {
        this.setModelObject(value)
      }
    }
  },
  created() {
    if (this.hasOptGroups) {
      this.optionGroups = {}
      each(this.options, option => {
        if (option.header && !includes(this.optionGroups, option.header)) {
          this.optionGroups[option.key] = []
        } else {
          this.optionGroups[option.group].push(option)
        }
      })
    }
  },
  methods: {
    getLabel: option => option.name || option.label.primary,
    listItemId(item) {
      if (item.header) {
        return this.normalizeId(`${this.type}-option-group-${item.header}`)
      }
      return this.normalizeId(`${this.type}-option-${item.key}`)
    },
    normalizeId: id => id.toLowerCase().replace(/\W/g, ' ').trim().replace(/[ ]+/g, '-')
  }
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
