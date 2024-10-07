<template>
  <form id="unit-requirement-form" @submit.prevent="create">
    <div>
      <label
        id="label-of-name-input"
        for="unit-requirement-name-input"
        class="font-weight-bold mb-1"
      >
        Fulfillment Requirement Name (required)
      </label>
      <v-text-field
        id="unit-requirement-name-input"
        v-model="name"
        :aria-invalid="!name"
        aria-required="true"
        class="unit-requirement-name"
        hide-details
        maxlength="255"
        required
        @keydown.enter="unitRequirement ? update : create"
      />
      <div class="pl-2">
        <span class="text-surface-variant font-size-12">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
        <span
          v-if="name.length === 255"
          aria-live="polite"
          class="sr-only"
          role="alert"
        >
          Fulfillment requirement name cannot exceed 255 characters.
        </span>
      </div>
      <v-expand-transition>
        <div
          v-if="nameErrorMessage"
          aria-live="polite"
          class="text-error font-size-12"
          role="alert"
        >
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
        :set-units-lower="units => minUnits = units"
        :units-lower="minUnits"
      />
    </div>
    <div class="d-flex justify-end flex-wrap">
      <v-btn
        v-if="!unitRequirement"
        id="create-unit-requirement-btn"
        class="mt-2 mr-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Create Unit Requirement"
        @click.prevent="create"
      />
      <v-btn
        v-if="unitRequirement"
        id="update-unit-requirement-btn"
        class="mt-2 mr-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Save Unit Requirement"
        @click.prevent="update"
      />
      <v-btn
        id="cancel-create-unit-requirement-btn"
        class="mt-2"
        color="primary"
        text="Cancel"
        variant="outlined"
        @click.prevent="cancel"
      />
    </div>
  </form>
</template>

<script setup>
import UnitsInput from '@/components/degree/UnitsInput'
import {addUnitRequirement, updateUnitRequirement} from '@/api/degree'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {computed, onMounted, ref} from 'vue'
import {filter as _filter, get, isEmpty, map, trim} from 'lodash'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/utils'
import {useDegreeStore} from '@/stores/degree-edit-session/index'
import {validateUnitRange} from '@/lib/degree-progress'

const props = defineProps({
  onExit: {
    required: true,
    type: Function
  },
  unitRequirement: {
    default: undefined,
    required: false,
    type: Object
  }
})

const degreeStore = useDegreeStore()

const isSaving = ref(false)
const name = ref(get(props.unitRequirement, 'name') || '')
const minUnits = ref(get(props.unitRequirement, 'minUnits'))
const otherUnitRequirements = ref(
  props.unitRequirement ?
    _filter(degreeStore.unitRequirements, u => u.id !== get(props.unitRequirement, 'id')) :
    degreeStore.unitRequirements
)

onMounted(() => {
  alertScreenReader(props.unitRequirement ? `Edit "${name.value}" unit requirement` : 'Create unit requirement')
  putFocusNextTick('unit-requirement-name-input')
})

const disableSaveButton = computed(() => {
  return isSaving.value || !name.value || !!unitsErrorMessage.value || !!nameErrorMessage.value
})

const unitsErrorMessage = computed(() => {
  return isEmpty(trim(minUnits.value)) ? 'Required' : validateUnitRange(minUnits.value, undefined, 100).message
})

const nameErrorMessage = computed(() => {
  let message = undefined
  if (name.value) {
    const lowerCase = name.value.toLowerCase()
    const existingNames = map(otherUnitRequirements.value, u => u.name.toLowerCase())
    if (existingNames.findIndex(existingName => lowerCase === existingName) > -1) {
      message = 'Name cannot match the name of an existing Unit Requirement.'
    }
  }
  return message
})

const cancel = () => {
  alertScreenReader('Canceled.')
  isSaving.value = false
  props.onExit()
}

const create = () => {
  if (degreeStore.disableSaveButton) {
    putFocusRequiredField()
  } else {
    alertScreenReader('Saving')
    isSaving.value = true
    addUnitRequirement(degreeStore.templateId, name.value, minUnits.value).then(() => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        alertScreenReader(`Created "${name.value}" unit requirement.`)
        props.onExit()
      })
    })
  }
}
const putFocusRequiredField = () => {
  putFocusNextTick(name.value ? 'unit-requirement-min-units-input' : 'unit-requirement-name-input')
  alertScreenReader(`${name.value ? 'Units value' : 'Name'} required.`)
}

const update = () => {
  if (degreeStore.disableSaveButton) {
    putFocusRequiredField()
  } else {
    alertScreenReader('Saving')
    isSaving.value = true
    updateUnitRequirement(props.unitRequirement.id, name.value, minUnits.value).then(() => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        isSaving.value = false
        alertScreenReader(`Updated ${name.value} unit requirement.`)
        props.onExit()
      })
    })
  }
}
</script>
