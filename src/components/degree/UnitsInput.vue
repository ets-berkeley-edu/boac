<template>
  <div>
    <div class="d-flex">
      <label id="units-input-label" :class="labelClass" :for="inputId">
        {{ label }}
      </label>
      <div v-if="range" class="font-size-12">
        [<b-btn
          id="show-upper-units-input"
          class="toggle-btn"
          size="sm"
          variant="link"
          @click="toggle"
        >
          {{ showUnitsUpperInput ? 'hide range' : 'show range' }}
        </b-btn>]
      </div>
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <b-form-input
          :id="inputId"
          :aria-invalid="!isValidUnits(unitsLower, max)"
          aria-labelledby="units-input-label"
          class="units-input"
          :disabled="disable"
          maxlength="4"
          size="sm"
          trim
          :value="unitsLower"
          @input="setUnitsLower"
          @keypress.enter="onSubmit"
          @keyup.esc="onEscape"
        />
      </div>
      <div v-if="showUnitsUpperInput" class="pr-2 pt-1">
        to
      </div>
      <div v-if="showUnitsUpperInput">
        <b-form-input
          :id="`upper-${inputId}`"
          :aria-invalid="!isValidUnits(unitsUpper)"
          aria-labelledby="units-input-label"
          class="units-input"
          :disabled="disable"
          maxlength="4"
          size="sm"
          trim
          :value="unitsUpper"
          @input="setUnitsUpper"
          @keypress.enter="onSubmit"
        />
      </div>
    </div>
    <b-collapse :visible="!!errorMessage">
      <span class="text-error text-grey font-size-12">
        {{ errorMessage }}
      </span>
    </b-collapse>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import Util from '@/mixins/Util'
import {isValidUnits} from '@/lib/degree-progress'

export default {
  name: 'UnitsInput',
  mixins: [Context, DegreeEditSession, Util],
  props: {
    disable: {
      required: false,
      type: Boolean
    },
    errorMessage: {
      default: undefined,
      required: false,
      type: String
    },
    inputId: {
      default: 'units-input',
      required: false,
      type: String
    },
    label: {
      default: 'Units',
      required: false,
      type: String
    },
    labelClass: {
      default: 'font-weight-500 mb-1 pr-2',
      required: false,
      type: String
    },
    max: {
      default: 10,
      required: false,
      type: Number
    },
    onEscape: {
      default: () => {},
      required: false,
      type: Function
    },
    onSubmit: {
      required: true,
      type: Function
    },
    range: {
      required: false,
      type: Boolean
    },
    required: {
      required: false,
      type: Boolean
    },
    setUnitsLower: {
      required: true,
      type: Function
    },
    setUnitsUpper: {
      default: () => {},
      required: false,
      type: Function
    },
    unitsLower: {
      default: undefined,
      required: false,
      type: [Number, String, undefined]
    },
    unitsUpper: {
      default: undefined,
      required: false,
      type: [Number, String, undefined]
    }
  },
  data: () => ({
    showUnitsUpperInput: false
  }),
  created() {
    this.showUnitsUpperInput = !!this.unitsUpper && this.unitsLower !== this.unitsUpper
    if (!this.showUnitsUpperInput) {
      this.setUnitsUpper(undefined)
    }
  },
  methods: {
    isValidUnits,
    toggle() {
      this.showUnitsUpperInput = !this.showUnitsUpperInput
      if (!this.showUnitsUpperInput) {
        this.setUnitsUpper(undefined)
      }
      this.putFocusNextTick(this.showUnitsUpperInput && this.unitsLower ? `upper-${this.inputId}` : this.inputId)
      this.alertScreenReader(`Enter ${this.showUnitsUpperInput ? 'end' : 'start'} value of range.`)
    }
  }
}
</script>

<style scoped>
.toggle-btn {
  padding: 0 1px 0 1px;
}
.units-input {
  width: 3rem;
}
</style>
