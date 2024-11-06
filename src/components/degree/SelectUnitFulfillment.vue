<template>
  <div>
    <select
      :id="`column-${position}-unit-requirement-select`"
      v-model="model"
      class="select-menu w-100"
      :disabled="disable"
      @change="onChangeUnitRequirement"
    >
      <option :id="`column-${position}-unit-requirement-option-null`" :value="null">
        Choose...
      </option>
      <option
        v-for="(option, index) in degreeStore.unitRequirements"
        :id="`column-${position}-unit-requirement-option-${index}`"
        :key="index"
        :disabled="includes(map(selectedUnitRequirements, 'id'), option.id)"
        :value="option"
      >
        {{ option.name }}
      </option>
    </select>
    <div v-if="size(selectedUnitRequirements)" class="w-100">
      <label
        :for="`column-${position}-unit-requirement-list`"
        class="sr-only"
      >
        Selected Requirement Fulfillment(s)
      </label>
      <ul
        :id="`column-${position}-unit-requirement-list`"
        class="mb-2 list-no-bullets pl-0"
      >
        <li
          v-for="(unitRequirement, index) in selectedUnitRequirements"
          :id="`column-${position}-unit-requirement-${index}`"
          :key="index"
          class="list-item text-medium-emphasis"
        >
          <div class="d-flex align-center justify-space-between">
            <div class="truncate-with-ellipsis">
              {{ unitRequirement.name }}
            </div>
            <div class="float-right">
              <v-btn
                :id="`column-${position}-unit-requirement-remove-${index}`"
                :aria-label="`Remove ${unitRequirement.name} from Unit Requirements`"
                color="error"
                density="compact"
                :disabled="disable"
                :icon="mdiCloseCircleOutline"
                title="Remove"
                variant="text"
                @click="() => removeUnitRequirement(unitRequirement, index)"
              ></v-btn>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {includes, map, remove, size} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'
import {ref} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const degreeStore = useDegreeStore()

const props = defineProps({
  disable: {
    required: false,
    type: Boolean
  },
  onUnitRequirementsChange: {
    required: true,
    type: Function
  },
  position: {
    required: true,
    type: Number
  },
  selectedUnitRequirements: {
    default: undefined,
    required: false,
    type: Array
  }
})

const model = ref(null)

const onChangeUnitRequirement = () => {
  props.onUnitRequirementsChange(props.selectedUnitRequirements.concat([model.value]))
  alertScreenReader(`${model.value.name} selected`)
  model.value = null
}

const removeUnitRequirement = (item, index) => {
  const lastItemIndex = size(props.selectedUnitRequirements) - 1
  props.onUnitRequirementsChange(remove(props.selectedUnitRequirements, s => s.id !== item.id))
  if (lastItemIndex > 0) {
    const nextFocusIndex = (index === lastItemIndex ) ? index - 1 : index
    putFocusNextTick(`column-${props.position}-unit-requirement-remove-${nextFocusIndex}`)
  } else {
    putFocusNextTick(`column-${props.position}-unit-requirement-select`)
  }
  alertScreenReader(`${item.name} removed`)
}
</script>

<style scoped>
.list-item {
  border-radius: 5px;
  border: 1px solid rgba(var(--v-border-color), var(--v-disabled-opacity));
  height: 36px;
  margin-top: 6px;
  padding: 3px 8px;
  min-width: 50%;
}
</style>
