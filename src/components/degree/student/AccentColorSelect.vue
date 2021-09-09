<template>
  <div>
    <div>
      <label
        for="color-code-select"
        class="font-weight-500"
      >
        Color Code
      </label>
    </div>
    <div>
      <b-dropdown
        id="color-code-select"
        v-model="selected"
        block
        class="mb-2 ml-0"
        menu-class="w-100"
        :toggle-class="`align-items-center border-base border-color-${selected ? selected.toLowerCase() : 'lightgrey'} d-flex justify-content-between transparent`"
        variant="close-white"
      >
        <template #button-content>
          <div
            v-if="selected"
            class="align-items-center d-flex"
            :class="`accent-color-${selected.toLowerCase()}`"
          >
            <div class="pr-2">
              <font-awesome icon="square" />
            </div>
            <div>
              {{ selected }}
            </div>
          </div>
          <span v-if="!selected">Choose...</span>
        </template>
        <b-dropdown-item
          v-if="!!selected"
          id="border-color-none"
          @click="setSelected(undefined)"
        >
          <span class="text-secondary">-- None --</span>
        </b-dropdown-item>
        <b-dropdown-item
          v-for="(hexCode, colorName) in $_.omit($config.degreeProgressColorCodes, [selected])"
          :id="`color-code-${colorName.toLowerCase()}-option`"
          :key="hexCode"
          @click="setSelected(colorName)"
        >
          <div class="align-items-center d-flex" :class="`accent-color-${colorName.toLowerCase()}`">
            <div class="pr-2">
              <font-awesome icon="square" />
            </div>
            <div>
              {{ colorName }}
            </div>
          </div>
        </b-dropdown-item>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AccentColorSelect',
  props: {
    accentColor: {
      default: undefined,
      type: String
    },
    onChange: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    selected: undefined
  }),
  created() {
    this.selected = this.accentColor
  },
  methods: {
    setSelected(value) {
      this.selected = value
      this.onChange(this.selected)
      this.$announcer.polite(`${this.selected} selected`)
    }
  }
}
</script>

<style>
.border-base {
  border: 1px solid;
}
.border-color-blue {
  border-color: #005c91 !important;
}
.border-color-green {
  border-color: #36a600 !important;
}
.border-color-lightgrey {
  border-color: #aaa !important;
}
.border-color-orange {
  border-color: #e48600 !important;
}
.border-color-purple {
  border-color: #b300c5 !important;
}
.border-color-red {
  border-color: #d0021b !important;
}
</style>