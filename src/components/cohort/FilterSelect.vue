<template>
  <div>
    <v-select
      :id="`filter-select-${type}-${filterRowIndex}`"
      v-model="vModelProxy"
      :aria-labelledby="labelledby"
      class="select-menu"
      density="compact"
      :disabled="!options"
      eager
      hide-details
      item-title="name"
      :items="options"
      persistent-hint
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
          v-else
          :id="listItemId(item.raw.value)"
          v-bind="props"
          :aria-describedby="item.raw.group ? listItemId({header: item.raw.group}) : false"
          class="min-height-unset py-1 pl-8"
          density="compact"
          role="option"
          :title="item.title"
        ></v-list-item>
      </template>
    </v-select>
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

<style scoped>
.select-menu {
  background-color: #fff;
  height: 44px;
  width: 320px;
}
</style>
