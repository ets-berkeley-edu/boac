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
        :disabled="$_.includes($_.map(selected, 'id'), option.id)"
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
          <div class="align-items-center d-flex justify-content-between mr-3 mt-1 pill-unit-requirement">
            <div class="pb-1">
              {{ unitRequirement.name }}
            </div>
            <div>
              <b-btn
                :id="`column-${position}-unit-requirement-remove-${index}`"
                :disabled="disable"
                class="pb-0 px-0 pt-1"
                variant="link"
                @click="removeUnitRequirement(unitRequirement)"
              >
                <font-awesome icon="times-circle" class="font-size-24 has-error pl-2" />
                <span class="sr-only">Remove</span>
              </b-btn>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import DegreeEditSession from '@/mixins/DegreeEditSession'

export default {
  name: 'SelectUnitFulfillment',
  mixins: [DegreeEditSession],
  props: {
    disable: {
      required: false,
      type: Boolean
    },
    initialUnitRequirements: {
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
    this.selected = this.$_.cloneDeep(this.initialUnitRequirements)
  },
  methods: {
    onChangeUnitRequirement(option) {
      this.$announcer.polite(option ? `${option.name} selected` : 'Unselected')
      if (option) {
        this.selected.push(option)
        this.onUnitRequirementsChange(this.selected)
        this.model = null
      }
    },
    removeUnitRequirement(item) {
      this.$announcer.polite(`${item.name} removed`)
      this.selected = this.$_.remove(this.selected, selected => selected.id !== item.id)
      this.onUnitRequirementsChange(this.selected)
    }
  }
}
</script>

<style scoped>
.pill-unit-requirement {
  background-color: #fff;
  border: 1px solid #999;
  border-radius: 5px;
  color: #666;
  margin-top: 8px;
  padding: 4px 12px 4px 12px;
  width: auto;
}
</style>
