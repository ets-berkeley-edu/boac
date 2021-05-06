<template>
  <div>
    <div class="d-flex">
      <label id="units-input-label" :for="inputIdLower" class="font-weight-500 pr-2">
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
          {{ showUnitsUpperInput ? 'single input' : 'range' }}
        </b-btn>]
      </div>
    </div>
    <div class="d-flex">
      <div class="pr-2">
        <b-form-input
          :id="inputIdLower"
          v-model="unitsLower"
          aria-labelledby="units-input-label"
          :aria-invalid="!isValid(unitsLower)"
          class="units-input"
          :disabled="disable"
          maxlength="3"
          size="sm"
          trim
          @input="onUnitsInput"
          @keypress.enter="onKeypressEnter"
        />
      </div>
      <div v-if="showUnitsUpperInput" class="pr-2 pt-1">
        to
      </div>
      <div v-if="showUnitsUpperInput">
        <b-form-input
          :id="inputIdUpper"
          v-model="unitsUpper"
          :aria-invalid="!isValid(unitsUpper)"
          aria-labelledby="units-input-label"
          class="units-input"
          :disabled="disable"
          maxlength="3"
          size="sm"
          trim
          @input="onUnitsInput"
          @keypress.enter="onKeypressEnter"
        />
      </div>
    </div>
    <span v-if="errorMessage" class="has-error faint-text font-size-12">
      {{ errorMessage }}
    </span>
  </div>
</template>

<script>
import Util from '@/mixins/Util'

export default {
  name: 'UnitsInput',
  mixins: [Util],
  props: {
    disable: {
      required: false,
      type: Boolean
    },
    id: {
      default: 'units-input',
      required: false,
      type: String
    },
    label: {
      default: 'Units',
      required: false,
      type: String
    },
    max: {
      default: 10,
      required: false,
      type: Number
    },
    onKeypressEnter: {
      default: () => {},
      required: false,
      type: Function
    },
    onInput: {
      default: () => {},
      required: false,
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
    units: {
      required: false,
      type: [Number, String, Array]
    }
  },
  data: () => ({
    inputIdLower: undefined,
    inputIdUpper: undefined,
    showUnitsUpperInput: false,
    unitsLower: '',
    unitsUpper: ''
  }),
  computed: {
    errorMessage() {
      if (this.isValid(this.unitsLower)) {
        if (this.showUnitsUpperInput) {
          if (this.isValid(this.unitsUpper)) {
            const empty = this.$_.isEmpty(this.unitsLower) && this.$_.isEmpty(this.unitsUpper)
            return empty || parseFloat(this.unitsLower) <= parseFloat(this.unitsUpper) ? null : 'Invalid range'
          } else {
            return 'Invalid upper range value'
          }
        } else {
          return null
        }
      } else {
        return this.showUnitsUpperInput ? 'Invalid lower range value.' : 'Invalid'
      }
    }
  },
  created() {
    this.inputIdLower = this.range ? `lower-${this.id}` : this.id
    this.inputIdUpper = `upper-${this.id}`
    if (Array.isArray(this.units)) {
      this.unitsLower = this.units.length > 0 ? this.units[0] : undefined
      this.unitsUpper = this.units.length > 1 ? this.units[1] : undefined
      this.showUnitsUpperInput = this.unitsLower !== this.unitsUpper
    } else {
      this.unitsLower = this.units
    }
    this.onInput(!this.errorMessage, this.unitsLower, this.unitsUpper)
  },
  methods: {
    isValid(units) {
      if (this.$_.isEmpty(units)) {
        return !this.required
      }
      return !isNaN(units) && units >= 0 && units <= this.max
    },
    onUnitsInput() {
      this.onInput(!this.errorMessage, this.unitsLower, this.unitsUpper)
    },
    toggle() {
      this.showUnitsUpperInput = !this.showUnitsUpperInput
      this.putFocusNextTick(this.showUnitsUpperInput && this.unitsLower ? this.inputIdUpper : this.inputIdLower)
      this.$announcer.polite(`Enter ${this.showUnitsUpperInput ? 'end' : 'start'} value of range.`)
    }
  }
}
</script>

<style scoped>
.toggle-btn {
  padding: 0 2px 0 2px;
}
.units-input {
  text-align: center;
  max-width: 2.5rem;
}
</style>
