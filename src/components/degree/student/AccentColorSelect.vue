<template>
  <div>
    <div class="mb-1">
      <label
        for="color-code-select"
        class="font-weight-bold"
      >
        Color Code
      </label>
    </div>
    <v-menu @update:model-value="onOpenMenu">
      <template #activator="{props: menuProps}">
        <button
          id="color-code-select"
          class="select-menu w-100"
          :class="getCssClass('border', selected)"
          v-bind="menuProps"
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
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {find, map, toLower} from 'lodash'
import {mdiSquare} from '@mdi/js'
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
  },
  onOpenMenu: {
    default: () => {},
    required: false,
    type: Function
  }
})

const contextStore = useContextStore()
const noneSelected = {title: '-- None --', color: undefined}
const items = [noneSelected].concat(map(contextStore.config.degreeProgressColorCodes, (color, title) => ({title, color})))
const selected = ref(find(items, ['color', props.accentColor ? toLower(props.accentColor) : undefined]))

const getCssClass = (type, option) => `${type}-color-${option.color}`

const setSelected = value => {
  selected.value = value
  props.onChange(selected.value ? selected.value.color : undefined)
  alertScreenReader(`${selected.value ? selected.value.color : 'None' } selected`)
  putFocusNextTick('color-code-select')
}
</script>

<style>
.border-base {
  border: 1px solid;
}
.border-color-blue {
  border-color: rgb(var(--v-theme-accent-blue)) !important;
}
.border-color-green {
  border-color: rgb(var(--v-theme-accent-green)) !important;
}
.border-color-orange {
  border-color: rgb(var(--v-theme-accent-orange)) !important;
}
.border-color-purple {
  border-color: rgb(var(--v-theme-accent-purple)) !important;
}
.border-color-red {
  border-color: rgb(var(--v-theme-accent-red)) !important;
}
</style>
