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
    <select
      id="color-code-select"
      v-model="selected"
      class="select-menu w-100"
    >
      <option class="line2" :value="undefined" @select="setSelected(undefined)">
        Choose...
      </option>
      <option
        v-for="(hexCode, colorName) in contextStore.config.degreeProgressColorCodes"
        :id="`color-code-${colorName.toLowerCase()}-option`"
        :key="hexCode"
        @select="setSelected(colorName)"
      >
        <span :class="`accent-color-${toLower(selected)}`">
          <v-icon :icon="mdiSquareOutline" />
          {{ colorName }}
        </span>
      </option>
    </select>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {mdiSquareOutline} from '@mdi/js'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {toLower} from 'lodash'

const props = defineProps({
  accentColor: {
    default: undefined,
    type: [String, undefined]
  },
  onChange: {
    required: true,
    type: Function
  }
})

const contextStore = useContextStore()
const selected = ref(props.accentColor)

const setSelected = value => {
  selected.value = value
  props.onChange(selected.value)
  alertScreenReader(`${selected.value} selected`)
}
</script>

<style>
option.line1 {
	background-color: #000000;
	color: #ffffff;
}

option.line2 {
	background-color: #000000;
	color: #ffff00;
}
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
