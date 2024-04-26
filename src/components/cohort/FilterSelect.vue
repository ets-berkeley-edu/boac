<template>
  <v-select
    :id="`filter-select-${type}-${filterRowIndex}`"
    v-model="vModelProxy"
    :aria-labelledby="labelledby"
    bg-color="white"
    class="filter-select"
    :class="{'border-left-primary': hasLeftBorderStyle}"
    color="primary"
    :disabled="!options"
    eager
    hide-details
    item-title="name"
    item-value="key"
    :items="options"
    persistent-hint
    placeholder="Select.."
    return-object
    single-line
    variant="outlined"
  >
    <template #item="{props, item}">
      <v-list-subheader
        v-if="item.raw.header"
        :id="listItemId(item)"
      >
        {{ item.raw.header }}
      </v-list-subheader>
      <v-list-item
        v-if="!item.raw.header"
        :id="listItemId(item.raw)"
        v-bind="props"
        :aria-describedby="item.raw.group ? listItemId({header: item.raw.group}) : false"
        class="min-height-unset py-1 pl-8"
        density="comfortable"
        role="option"
        :title="item.title"
      />
    </template>
  </v-select>
</template>

<script>
export default {
  name: 'FilterSelect',
  props: {
    hasLeftBorderStyle: {
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
.border-left-primary .v-field {
  border-bottom-left-radius: 0;
  border-top-left-radius: 0;
  border-left: 6px solid rgb(var(--v-theme-primary));
}
</style>

<style scoped>
.filter-select {
  height: 56px;
  white-space: nowrap;
  width: 320px;
}
</style>
