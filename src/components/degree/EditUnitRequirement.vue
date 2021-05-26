<template>
  <form id="unit-requirement-form" @submit.prevent="create">
    <div class="d-flex flex-column pb-3">
      <label
        id="label-of-name-input"
        for="unit-requirement-name-input"
        class="font-weight-bolder"
      >Fulfillment Requirement Name (required)</label>
      <input
        id="unit-requirement-name-input"
        v-model.trim="name"
        class="form-control unit-requirement-name"
        aria-labelledby="label-of-name-input"
        :aria-invalid="!name"
        aria-required="true"
        maxlength="255"
        required
        type="text"
        @keypress.enter="() => $_.isNil(index) ? create() : update()"
      />
      <div class="pl-2">
        <span class="faint-text font-size-12">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
        <span v-if="name.length === 255" class="sr-only" aria-live="polite">
          Fulfillment requirement name cannot exceed 255 characters.
        </span>
      </div>
    </div>
    <div class="d-flex flex-column pb-3">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        input-id="unit-requirement-min-units-input"
        label="Minimum Units (required)"
        :max="100"
        :on-submit="() => $_.isNil(index) ? create() : update()"
        :set-units-lower="setMinUnits"
        :units-lower="minUnits"
      />
    </div>
    <b-btn
      v-if="$_.isNil(index)"
      id="create-unit-requirement-btn"
      :disabled="disableSaveButton"
      class="btn-primary-color-override"
      variant="primary"
      @click.prevent="create"
    >
      Create Unit Requirement
    </b-btn>
    <b-btn
      v-if="!$_.isNil(index)"
      id="update-unit-requirement-btn"
      :disabled="disableSaveButton"
      class="btn-primary-color-override"
      variant="primary"
      @click.prevent="update"
    >
      Save Unit Requirement
    </b-btn>
    <b-btn
      id="cancel-create-unit-requirement-btn"
      variant="link"
      @click.prevent="cancel"
    >
      Cancel
    </b-btn>
  </form>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'

export default {
  name: 'EditUnitRequirement',
  mixins: [Context, DegreeEditSession, Util],
  components: {UnitsInput},
  props: {
    index: {
      default: undefined,
      required: false,
      type: [Number, String]
    },
    onExit: {
      required: true,
      type: Function
    },
    unitRequirement: {
      required: false,
      type: Object
    }
  },
  data: () => ({
    isSaving: false,
    name: '',
    minUnits: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving || !this.name || !!this.unitsErrorMessage
    },
    unitsErrorMessage() {
      const isEmpty = this.$_.isEmpty(this.$_.trim(this.minUnits))
      return isEmpty ? 'Required' : this.validateUnitRange(this.minUnits, undefined, 100).message
    }
  },
  created() {
    if (this.unitRequirement) {
      this.name = this.unitRequirement.name
      this.minUnits = this.unitRequirement.minUnits
      this.alertScreenReader(`Edit unit requirement ${this.name}`)
    } else {
      this.alertScreenReader('Create unit requirement')
    }
    this.putFocusNextTick('unit-requirement-name-input')
  },
  methods: {
    cancel() {
      this.$announcer.polite('Canceled.')
      this.isSaving = false
      this.onExit()
    },
    create() {
      if (this.disableSaveButton) {
        this.putFocusRequiredField()
      } else {
        this.$announcer.polite('Saving')
        this.isSaving = true
        this.createUnitRequirement({
          name: this.name,
          minUnits: this.minUnits
        }).then(() => {
          this.$announcer.polite(`Created ${this.name}.`)
          this.onExit()
        })
      }
    },
    putFocusRequiredField() {
      this.putFocusNextTick(this.name ? 'unit-requirement-min-units-input' : 'unit-requirement-name-input')
      this.$announcer.polite(`${this.name ? 'Units value' : 'Name'} required.`)
    },
    setMinUnits(units) {
      this.minUnits = units
    },
    update() {
      if (this.disableSaveButton) {
        this.putFocusRequiredField()
      } else {
        this.$announcer.polite('Saving')
        this.isSaving = true
        this.updateUnitRequirement({
          index: this.index,
          name: this.name,
          minUnits: this.minUnits
        }).then(() => {
          this.isSaving = false
          this.$announcer.polite(`Updated ${this.name}.`)
          this.onExit()
        })
      }
    }
  }
}
</script>

<style scoped>
.unit-requirement-name {
  width: 22rem;
}
</style>
