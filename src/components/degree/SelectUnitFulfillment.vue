<template>
  <div>
    <b-select
      :id="`column-${position}-unit-requirement-select`"
      v-model="model"
      :disabled="disable || (unitRequirements.length === selected.length)"
      @change="onChangeUnitRequirement"
    >
      <b-select-option :id="`column-${position}-unit-requirement-option-null`" :value="null">Choose...</b-select-option>
      <b-select-option
        v-for="(option, index) in unitRequirements"
        :id="`column-${position}-unit-requirement-option-${index}`"
        :key="index"
        :disabled="_includes(_map(selected, 'id'), option.id)"
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
              <b-btn
                :id="`column-${position}-unit-requirement-remove-${index}`"
                :disabled="disable"
                class="pill-list-btn px-0 py-0"
                variant="link"
                @click="removeUnitRequirement(unitRequirement)"
              >
                <v-icon
                  :icon="mdiCloseCircleOutline"
                  class="font-size-24 pl-2"
                  color="error"
                />
                <span class="sr-only">Remove</span>
              </b-btn>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import {mdiCloseCircleOutline} from '@mdi/js'
</script>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'

export default {
  name: 'SelectUnitFulfillment',
  mixins: [Context, DegreeEditSession, Util],
  props: {
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
  },
  data: () => ({
    selected: undefined,
    model: null
  }),
  created() {
    this.selected = this._cloneDeep(this.initialUnitRequirements)
  },
  methods: {
    onChangeUnitRequirement(option) {
      this.alertScreenReader(option ? `${option.name} selected` : 'Unselected')
      if (option) {
        this.selected.push(option)
        this.onUnitRequirementsChange(this.selected)
        this.model = null
      }
    },
    removeUnitRequirement(item) {
      this.alertScreenReader(`${item.name} removed`)
      this.selected = this._remove(this.selected, selected => selected.id !== item.id)
      this.onUnitRequirementsChange(this.selected)
    }
  }
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
