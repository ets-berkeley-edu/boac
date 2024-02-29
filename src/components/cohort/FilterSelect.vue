<template>
  <div>
    <b-select
      v-if="hasOptGroups(options)"
      :id="`filter-select-${type}-${filterRowIndex}`"
      v-model="vModelProxy"
      :aria-labelledby="labelledby"
      class="select-menu"
      :disabled="!options"
      @change="onSelectChange"
    >
      <b-select-option
        v-if="!vModelProxy"
        :id="`${type}-option-null`"
        :value="undefined"
      >
        Select...
      </b-select-option>
      <b-select-option-group
        v-for="(groupOptions, label) in options"
        :id="normalizeId(`${type}-option-group-${label}`)"
        :key="label"
        :label="label"
      >
        <b-select-option
          v-for="option in groupOptions"
          :id="normalizeId(`${type}-option-${option.value}`)"
          :key="option.key"
          :aria-disabled="option.disabled"
          class="h-100"
          :disabled="option.disabled"
          :value="option"
        >
          {{ getLabel(option) }}
        </b-select-option>
      </b-select-option-group>
    </b-select>
    <b-select
      v-if="!hasOptGroups(options)"
      :id="normalizeId(`filter-select-${type}-${filterRowIndex}`)"
      v-model="vModelProxy"
      :aria-labelledby="labelledby"
      class="select-menu"
      @change="onSelectChange"
    >
      <b-select-option
        v-if="!vModelProxy"
        :id="`${type}-option-null`"
        :value="undefined"
      >
        Select...
      </b-select-option>
      <b-select-option
        v-for="option in options"
        :id="normalizeId(`${type}-option-${option.value}`)"
        :key="option.key"
        class="h-100"
        :disabled="option.disabled"
        :value="option"
      >
        {{ getLabel(option) }}
      </b-select-option>
    </b-select>
  </div>
</template>

<script>
export default {
  name: 'FilterSelect',
  props: {
    filterRowIndex: {
      required: true,
      type: [Number, String]
    },
    labelledby: {
      required: true,
      type: String
    },
    onSelectChange: {
      required: true,
      type: Function
    },
    options: {
      default: undefined,
      required: false,
      type: [Object, Array, undefined]
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
  methods: {
    getLabel: option => option.name || option.label.primary,
    hasOptGroups: options => !Array.isArray(options),
    normalizeId: id => id.toLowerCase().replace(/\W/g, ' ').trim().replace(/[ ]+/g, '-')
  }
}
</script>

<style scoped>
.select-menu {
  background-color: #fff;
  height: 44px;
  width: 320px;
}
</style>
