<template>
  <form id="unit-requirement-form" @submit.prevent="create">
    <div class="pt-1">
      <label
        id="label-of-name-input"
        for="unit-requirement-name-input"
        class="font-weight-500 mb-1"
      >
        Fulfillment Requirement Name (required)
      </label>
      <v-text-field
        id="unit-requirement-name-input"
        v-model="name"
        aria-describedby="unit-requirement-name-input-messages"
        :aria-invalid="!name"
        aria-required="true"
        autocomplete="on"
        class="unit-requirement-name"
        :error="!!nameErrorMessage"
        :error-messages="nameErrorMessage"
        maxlength="255"
        persistent-counter
        required
        @keydown.enter="unitRequirement ? update : create"
        @update:model-value="() => nameErrorMessage = null"
      >
        <template #counter="{max, value}">
          <CharacterCount :count="toInt(value)" id-prefix="unit-requirement-name" :max="toInt(max)" />
        </template>
        <template #message="{message}">
          <v-alert
            id="unit-requirement-name-error"
            class="font-size-14 line-height-normal"
            density="compact"
            role="none"
            :text="message"
            type="error"
            variant="tonal"
          />
        </template>
      </v-text-field>
    </div>
    <div class="pt-1">
      <UnitsInput
        :disable="isSaving"
        :error="!!unitsErrorMessage"
        :error-message="unitsErrorMessage"
        input-id="unit-requirement-min-units-input"
        label="Minimum Units (required)"
        :max="100"
        :on-submit="unitRequirement ? update : create"
        required
        :set-units-lower="setUnitsLower"
        :units-lower="minUnits"
      />
    </div>
    <div class="d-flex justify-end flex-wrap">
      <v-btn
        v-if="!unitRequirement"
        id="create-unit-requirement-btn"
        class="mt-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Create Unit Requirement"
        @click.prevent="create"
      />
      <v-btn
        v-if="unitRequirement"
        id="update-unit-requirement-btn"
        class="mt-2"
        color="primary"
        :disabled="disableSaveButton"
        text="Save Unit Requirement"
        @click.prevent="update"
      />
      <v-btn
        id="cancel-create-unit-requirement-btn"
        :aria-label="unitRequirement ? 'Cancel Edit Unit Requirement' : 'Cancel Create Unit Requirement'"
        class="ml-2 mt-2"
        color="primary"
        text="Cancel"
        variant="outlined"
        @click.prevent="cancel"
      />
    </div>
  </form>
</template>

<script setup>
import {computed, onMounted, ref} from 'vue'
import {filter as _filter, get, isEmpty, map, trim} from 'lodash'
import CharacterCount from '@/components/util/CharacterCount'
import UnitsInput from '@/components/degree/UnitsInput'
import {addUnitRequirement, updateUnitRequirement} from '@/api/degree'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {refreshDegreeTemplate} from '@/stores/degree-edit-session/degree-edit-session-utils'
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
const nameErrorMessage = ref(undefined)
const minUnits = ref(get(props.unitRequirement, 'minUnits'))
const otherUnitRequirements = ref(
  props.unitRequirement ?
    _filter(degreeStore.unitRequirements, u => u.id !== get(props.unitRequirement, 'id')) :
    degreeStore.unitRequirements
)
const unitsErrorMessage = ref(undefined)

onMounted(() => {
  putFocusNextTick('unit-requirement-name-input')
})

const disableSaveButton = computed(() => {
  return isSaving.value || !name.value || !minUnits.value || !!unitsErrorMessage.value || !!nameErrorMessage.value
})

const cancel = () => {
  alertScreenReader('Canceled.')
  isSaving.value = false
  props.onExit()
}

const create = () => {
  if (validate()) {
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

const setUnitsLower = units => {
  minUnits.value = units
  unitsErrorMessage.value = null
}

const update = () => {
  if (validate()) {
    alertScreenReader('Saving')
    isSaving.value = true
    updateUnitRequirement(props.unitRequirement.id, name.value, minUnits.value).then(() => {
      refreshDegreeTemplate(degreeStore.templateId).then(() => {
        isSaving.value = false
        alertScreenReader(`Updated "${name.value}" unit requirement.`)
        props.onExit()
      })
    })
  }
}

const validate = () => {
  const requirementName = trim(name.value)
  if (requirementName) {
    const lowerCase = requirementName.toLowerCase()
    const existingNames = map(otherUnitRequirements.value, u => u.name.toLowerCase())
    if (existingNames.findIndex(existingName => lowerCase === existingName) > -1) {
      nameErrorMessage.value = `Degree has an existing unit requirement named '${requirementName}'. Please choose a different name.`
    }
  } else {
    nameErrorMessage.value = 'Name is required'
  }
  unitsErrorMessage.value = isEmpty(trim(minUnits.value)) ? 'Minimum Units is required' : validateUnitRange(minUnits.value, undefined, 100).message
  if (nameErrorMessage.value) {
    putFocusNextTick('unit-requirement-name-input')
  } else if (unitsErrorMessage.value) {
    putFocusNextTick('unit-requirement-min-units-input')
  } else {
    return true
  }
}
</script>
