<template>
  <div>
    <div class="mb-1">
      <label
        for="color-code-select"
        class="font-weight-700"
      >
        Color Code
      </label>
    </div>
    <v-menu>
      <template #activator="{props}">
        <button
          id="color-code-select"
          class="border-sm px-3 py-2 rounded-lg v-btn--variant-outlined w-100"
          :class="getCssClass('border', selected)"
          v-bind="props"
        >
          <div class="align-center d-flex">
            <div v-if="!selected.color" class="text-left">{{ selected.title }}</div>
            <div
              v-if="selected.color"
              class="align-center d-flex"
              :class="getCssClass('accent', selected)"
            >
              <v-icon :icon="mdiSquare" class="mr-2" :color="selected ? selected.color : 'black'" />
              <div>
                {{ selected.title }}
              </div>
            </div>
            <div class="ml-auto">
              <v-icon
                :color="selected ? selected.color : 'black'"
                :icon="props['aria-expanded'] === 'true' ? mdiMenuUp : mdiMenuDown"
              />
            </div>
          </div>
        </button>
      </template>
      <v-list>
        <v-list-item
          v-for="item in items"
          :id="`color-code-option-${item.color || 'none'}`"
          :key="item.color"
          density="compact"
          :base-color="item.color"
          :color="item.color"
          @click="() => setSelected(item)"
        >
          <div class="align-center d-flex" :class="getCssClass('accent', item)">
            <v-icon
              v-if="item.color"
              class="mr-2"
              :class="{'pl-3': !item.color}"
              :color="item.color"
              :icon="mdiSquare"
            />
            <div>
              {{ item.title }}
            </div>
          </div>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {find, map, toLower} from 'lodash'
import {mdiMenuDown, mdiMenuUp, mdiSquare} from '@mdi/js'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'

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
const noneSelected = {title: '-- None --', color: undefined}
const items = [noneSelected].concat(map(contextStore.config.degreeProgressColorCodes, (color, title) => ({title, color})))
const selected = ref(find(items, ['color', props.accentColor ? toLower(props.accentColor) : undefined]))

const getCssClass = (type, option) => `${type}-color-${option ? option.color : 'black'}`

const setSelected = value => {
  selected.value = value
  props.onChange(selected.value ? selected.value.color : undefined)
  alertScreenReader(`${selected.value ? selected.value.color : 'None' } selected`)
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
