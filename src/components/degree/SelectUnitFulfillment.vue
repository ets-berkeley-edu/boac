<template>
  <div>
    <b-select
      :id="`column-${position}-unit-requirement-select`"
      v-model="model"
      :disabled="disable || (degreeStore.unitRequirements.length === selected.length)"
      @change="onChangeUnitRequirement"
    >
      <b-select-option :id="`column-${position}-unit-requirement-option-null`" :value="null">Choose...</b-select-option>
      <b-select-option
        v-for="(option, index) in degreeStore.unitRequirements"
        :id="`column-${position}-unit-requirement-option-${index}`"
        :key="index"
        :disabled="includes(map(selected, 'id'), option.id)"
        :value="option"
      >
        {{ option.name }}
      </b-select-option>
    </b-select>
    <div v-if="selected.length">
      <label
        :for="`column-${position}-unit-requirement-list`"
        class="sr-only"
      >
        Selected Requirement Fulfillment(s)
      </label>
      <ul
        :id="`column-${position}-unit-requirement-list`"
        class="pill-list pl-0"
      >
        <li
          v-for="(unitRequirement, index) in selected"
          :id="`column-${position}-unit-requirement-${index}`"
          :key="index"
        >
          <div class="align-center d-flex justify-space-between mr-3 mt-2 pill-unit-requirement">
            <div>
              {{ unitRequirement.name }}
            </div>
            <div>
              <v-btn
                :id="`column-${position}-unit-requirement-remove-${index}`"
                :disabled="disable"
                class="pill-list-btn px-0 py-0"
                variant="text"
                @click="removeUnitRequirement(unitRequirement)"
              >
                <v-icon
                  :icon="mdiCloseCircleOutline"
                  class="font-size-24 pl-2"
                  color="error"
                />
                <span class="sr-only">Remove</span>
              </v-btn>
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
import {ref} from 'vue'
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
const selected = ref(cloneDeep(props.initialUnitRequirements))
const model = ref(null)

const onChangeUnitRequirement = option => {
  alertScreenReader(option ? `${option.name} selected` : 'Unselected')
  if (option) {
    selected.value.push(option)
    props.onUnitRequirementsChange(selected.value)
    model.value = null
  }
}

const removeUnitRequirement = item => {
  alertScreenReader(`${item.name} removed`)
  selected.value = remove(selected.value, selected => selected.id !== item.id)
  props.onUnitRequirementsChange(selected.value)
}
</script>

<style scoped>
.pill-list-btn {
  position: relative;
  top: 1px;
}
.pill-unit-requirement {
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 5px;
  color: #666;
  padding: 2px 12px 2px 12px;
  width: auto;
}
</style>
