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
    <v-menu>
      <template #activator="{props}">
        <button
          id="color-code-select"
          class="border-sm px-3 py-2 rounded-lg v-btn--variant-outlined w-100"
          :class="`border-color-${selected.value}`"
          v-bind="props"
        >
          <div class="align-center d-flex">
            <div v-if="!selected.value" class="text-left">{{ selected.title }}</div>
            <div
              v-if="selected.value"
              class="align-center d-flex"
              :class="`accent-color-${selected.value}`"
            >
              <v-icon :icon="mdiSquare" class="mr-2" :class="`accent-color-${selected.value}`" />
              <div>
                {{ selected.title }}
              </div>
            </div>
            <div class="ml-auto">
              <v-icon
                :color="selected.value"
                :icon="props['aria-expanded'] === 'true' ? mdiMenuUp : mdiMenuDown"
              />
            </div>
          </div>
        </button>
      </template>
      <v-list>
        <v-list-item
          v-for="item in items"
          :id="`color-code-option-${item.value || 'none'}`"
          :key="item.value"
          density="compact"
          :base-color="item.value"
          :color="item.value"
          @click="() => setSelected(item)"
        >
          <div v-if="!item.value" class="pl-3">{{ item.title }}</div>
          <div v-if="item.value" class="align-center d-flex" :class="`accent-color-${selected}`">
            <v-icon :icon="mdiSquare" class="mr-2" :class="`accent-color-${item.value}`" />
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
import {mdiMenuDown, mdiMenuUp, mdiSquare} from '@mdi/js'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {map} from 'lodash'

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
const noneSelected = {title: '-- None --', value: undefined}
const items = [noneSelected].concat(map(contextStore.config.degreeProgressColorCodes, (value, key) => ({title: key, value})))
const selected = ref(props.accentColor || noneSelected)

const setSelected = value => {
  selected.value = value
  props.onChange(selected.value)
  alertScreenReader(`${selected.value} selected`)
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
