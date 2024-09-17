<template>
  <div>
    <select
      :id="`column-${position}-unit-requirement-select`"
      v-model="model"
      class="select-menu w-100"
      :disabled="disable"
    >
      <option :id="`column-${position}-unit-requirement-option-null`" :value="null">
        Choose...
      </option>
      <option
        v-for="(option, index) in degreeStore.unitRequirements"
        :id="`column-${position}-unit-requirement-option-${index}`"
        :key="index"
        :disabled="includes(map(selected, 'id'), option.id)"
        :value="option"
      >
        {{ option.name }}
      </option>
    </select>
    <div v-if="selected.length" class="w-100">
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
          v-for="(unitRequirement, index) in selected"
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
                :aria-label="`Remove ${unitRequirement.name}`"
                color="error"
                density="compact"
                :disabled="disable"
                :icon="mdiCloseCircleOutline"
                title="Remove"
                variant="text"
                @click="() => removeUnitRequirement(unitRequirement)"
              ></v-btn>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {alertScreenReader} from '@/lib/utils'
import {cloneDeep, includes, map, remove} from 'lodash'
import {mdiCloseCircleOutline} from '@mdi/js'
import {ref, watch} from 'vue'
import {useDegreeStore} from '@/stores/degree-edit-session/index'

const degreeStore = useDegreeStore()

const props = defineProps({
  disable: {
    required: false,
    type: Boolean
  },
  initialUnitRequirements: {
    default: undefined,
    required: false,
    type: Array
  },
  onUnitRequirementsChange: {
    required: true,
    type: Function
  },
  position: {
    required: true,
    type: Number
  }
})

const model = ref(null)
const selected = ref(cloneDeep(props.initialUnitRequirements))

watch(model, () => {
  alertScreenReader(model.value ? `${model.value.name} selected` : 'Unselected')
  if (model.value) {
    selected.value.push(model.value)
    props.onUnitRequirementsChange(selected.value)
    model.value = null
  }
})

const removeUnitRequirement = item => {
  alertScreenReader(`${item.name} removed`)
  selected.value = remove(selected.value, selected => selected.id !== item.id)
  props.onUnitRequirementsChange(selected.value)
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
