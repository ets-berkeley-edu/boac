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
      <v-menu
        v-model="selected"
        block
        class="mb-2 ml-0"
        menu-class="w-100"
        :toggle-class="`align-center border-base border-color-${selected ? toLower(selected) : 'lightgrey'} d-flex justify-space-between transparent`"
        variant="close-white"
      >
        <template #activator="{props}">
          <v-btn
            id="color-code-select"
            class="align-center d-flex"
            :class="`accent-color-${toLower(selected)}`"
            v-bind="props"
          >
            <div class="pr-2">
              <v-icon :icon="mdiSquareOutline" />
            </div>
            <div>
              {{ selected }}
            </div>
          </v-btn>
          <span v-if="!selected">Choose...</span>
        </template>
        <v-list>
          <v-list-item-action v-if="!!selected">
            <v-btn
              id="border-color-none"
              class="text-medium-emphasis"
              variant="flat"
              @click="setSelected(undefined)"
            >
              -- None --
            </v-btn>
          </v-list-item-action>
          <v-list-item-action
            v-for="(hexCode, colorName) in omit(contextStore.config.degreeProgressColorCodes, [selected])"
            :key="hexCode"
          >
            <v-btn
              :id="`color-code-${colorName.toLowerCase()}-option`"
              variant="flat"
              @click="setSelected(colorName)"
            >
              <div class="align-center d-flex" :class="`accent-color-${colorName.toLowerCase()}`">
                <div class="pr-2">
                  <v-icon :icon="mdiSquareOutline" />
                </div>
                <div>
                  {{ colorName }}
                </div>
              </div>
            </v-btn>
          </v-list-item-action>
        </v-list>
      </v-menu>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {mdiSquareOutline} from '@mdi/js'
import {ref} from 'vue'
import {useContextStore} from '@/stores/context'
import {omit, toLower} from 'lodash'

const props = defineProps({
  accentColor: {
    default: undefined,
    type: String
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
