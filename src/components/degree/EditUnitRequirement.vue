<template>
  <form id="unit-requirement-form" @submit.prevent="create">
    <div>
      <label
        id="label-of-name-input"
        for="unit-requirement-name-input"
        class="font-weight-700 mb-1"
      >
        Fulfillment Requirement Name (required)
      </label>
      <v-text-field
        id="unit-requirement-name-input"
        v-model="name"
        :aria-invalid="!name"
        aria-required="true"
        class="unit-requirement-name"
        density="compact"
        hide-details
        maxlength="255"
        required
        variant="outlined"
        @keydown.enter="unitRequirement ? update : create"
      />
      <div class="pl-2">
        <span class="text-grey font-size-12">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
        <span v-if="name.length === 255" class="sr-only" aria-live="polite">
          Fulfillment requirement name cannot exceed 255 characters.
        </span>
      </div>
      <v-expand-transition>
        <div v-if="nameErrorMessage" class="text-error text-grey font-size-12">
          {{ nameErrorMessage }}
        </div>
      </v-expand-transition>
    </div>
    <div class="mt-1">
      <UnitsInput
        :disable="isSaving"
        :error-message="unitsErrorMessage"
        input-id="unit-requirement-min-units-input"
        label="Minimum Units (required)"
        :max="100"
        :on-submit="unitRequirement ? update : create"
        :set-units-lower="setMinUnits"
        :units-lower="minUnits"
      />
    </div>
    <div class="mt-2">
      <v-btn
        v-if="!unitRequirement"
        id="create-unit-requirement-btn"
        class="mr-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Create Unit Requirement"
        @click.prevent="create"
      />
      <v-btn
        v-if="unitRequirement"
        id="update-unit-requirement-btn"
        class="mr-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Save Unit Requirement"
        @click.prevent="update"
      />
      <v-btn
        id="cancel-create-unit-requirement-btn"
        color="primary"
        text="Cancel"
        variant="outlined"
        @click.prevent="cancel"
      />
    </div>
  </form>
</template>

<script>
import Context from '@/mixins/Context'
import DegreeEditSession from '@/mixins/DegreeEditSession'
import UnitsInput from '@/components/degree/UnitsInput'
import Util from '@/mixins/Util'
import {addUnitRequirement, updateUnitRequirement} from '@/api/degree'
import {alertScreenReader} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {validateUnitRange} from '@/lib/degree-progress'

export default {
  name: 'EditUnitRequirement',
  components: {UnitsInput},
  mixins: [Context, DegreeEditSession, Util],
  props: {
    onExit: {
      required: true,
      type: Function
    },
    unitRequirement: {
      default: undefined,
      required: false,
      type: Object
    }
  },
  data: () => ({
    isSaving: false,
    name: '',
    minUnits: undefined,
    otherUnitRequirements: undefined
  }),
  computed: {
    disableSaveButton() {
      return this.isSaving || !this.name || !!this.unitsErrorMessage || !!this.nameErrorMessage
    },
    unitsErrorMessage() {
      const isEmpty = this._isEmpty(this._trim(this.minUnits))
      return isEmpty ? 'Required' : validateUnitRange(this.minUnits, undefined, 100).message
    },
    nameErrorMessage() {
      let message = undefined
      if (this.name) {
        const lowerCase = this.name.toLowerCase()
        const existingNames = this._map(this.otherUnitRequirements, u => u.name.toLowerCase())
        if (existingNames.findIndex(existingName => lowerCase === existingName) > -1) {
          message = 'Name cannot match the name of an existing Unit Requirement.'
          alertScreenReader(message)
        }
      }
      return message
    }
  },
  created() {
    if (this.unitRequirement) {
      this.name = this.unitRequirement.name
      this.minUnits = this.unitRequirement.minUnits
      this.otherUnitRequirements = this._filter(this.unitRequirements, u => {
        return u.id !== this.unitRequirement.id
      })
      alertScreenReader(`Edit unit requirement ${this.name}`)
    } else {
      this.otherUnitRequirements = this.unitRequirements
      alertScreenReader('Create unit requirement')
    }
    this.putFocusNextTick('unit-requirement-name-input')
  },
  methods: {
    cancel() {
      alertScreenReader('Canceled.')
      this.isSaving = false
      this.onExit()
    },
    create() {
      if (this.disableSaveButton) {
        this.putFocusRequiredField()
      } else {
        alertScreenReader('Saving')
        this.isSaving = true
        addUnitRequirement(this.templateId, this.name, this.minUnits).then(() => {
          refreshDegreeTemplate(this.templateId).then(() => {
            alertScreenReader(`Created ${this.name}.`)
            this.onExit()
          })
        })
      }
    },
    putFocusRequiredField() {
      this.putFocusNextTick(this.name ? 'unit-requirement-min-units-input' : 'unit-requirement-name-input')
      alertScreenReader(`${this.name ? 'Units value' : 'Name'} required.`)
    },
    setMinUnits(units) {
      this.minUnits = units
    },
    update() {
      if (this.disableSaveButton) {
        this.putFocusRequiredField()
      } else {
        alertScreenReader('Saving')
        this.isSaving = true
        updateUnitRequirement(this.unitRequirement.id, this.name, this.minUnits).then(() => {
          refreshDegreeTemplate(this.templateId).then(() => {
            this.isSaving = false
            alertScreenReader(`Updated ${this.name}.`)
            this.onExit()
          })
        })
      }
    }
  }
}
</script>
