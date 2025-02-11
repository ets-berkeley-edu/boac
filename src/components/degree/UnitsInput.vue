<template>
  <div>
    <div class="align-center d-flex">
      <label id="units-input-label" :class="labelClass" :for="inputId">
        {{ label }}
      </label>
      <div v-if="range" class="d-flex font-size-14 pb-1">
        [<v-btn
          id="show-upper-units-input"
          :aria-expanded="showUnitsUpperInput"
          :aria-controls="`upper-${inputId}-container`"
          :aria-label="showUnitsUpperInput ? 'Hide Units Range' : 'Show Units Range'"
          class="align-self-center font-size-12 px-1 text-primary"
          density="compact"
          flat
          size="small"
          :text="showUnitsUpperInput ? 'hide range' : 'show range'"
          variant="text"
          width="5.5rem"
          @click="toggle"
        />]
      </div>
    </div>
    <div class="align-center d-flex">
      <div class="pr-2">
        <v-text-field
          :id="inputId"
          v-model="unitsLowerModel"
          :aria-describedby="`${inputId}-messages`"
          :aria-invalid="(required && !unitsLower) || !isValidUnits(unitsLower, max)"
          :aria-label="`Course Units${showUnitsUpperInput ? ', Start of Range' : ''}`"
          density="compact"
          :disabled="disable"
          hide-details
          maxlength="4"
          min-width="70"
          :required="required"
          @keydown.enter="onSubmit"
          @keyup.esc="onEscape"
          @update:model-value="setUnitsLower"
        />
      </div>
      <div v-if="showUnitsUpperInput" class="pr-2">
        to
      </div>
      <div v-show="showUnitsUpperInput" :id="`upper-${inputId}-container`">
        <v-text-field
          :id="`upper-${inputId}`"
          v-model="unitsUpperModel"
          :aria-describedby="`${inputId}-messages`"
          :aria-invalid="!isValidUnits(unitsUpper, MAX_UNITS_ALLOWED)"
          aria-label="Course Units, End of Range"
          density="compact"
          :disabled="disable"
          hide-details
          maxlength="4"
          min-width="70"
          @keydown.enter="onSubmit"
          @update:model-value="setUnitsUpper"
        />
      </div>
    </div>
    <v-expand-transition>
      <div
        v-show="!!errorMessage"
        :id="`${inputId}-messages`"
        aria-live="assertive"
        class="text-error font-size-12 pl-1"
        role="alert"
      >
        {{ errorMessage }}
      </div>
    </v-expand-transition>
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue'
import {putFocusNextTick} from '@/lib/utils'
import {MAX_UNITS_ALLOWED, isValidUnits} from '@/lib/degree-progress'

const props = defineProps({
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
})

const showUnitsUpperInput = ref(false)
const unitsLowerModel = ref(props.unitsLower)
const unitsUpperModel = ref(props.unitsUpper)

onMounted(() => {
  showUnitsUpperInput.value = !!props.unitsUpper && props.unitsLower !== props.unitsUpper
  if (!showUnitsUpperInput.value) {
    props.setUnitsUpper(undefined)
  }
})

const toggle = () => {
  showUnitsUpperInput.value = !showUnitsUpperInput.value
  if (!showUnitsUpperInput.value) {
    props.setUnitsUpper(undefined)
  }
  putFocusNextTick(showUnitsUpperInput.value && props.unitsLower ? `upper-${props.inputId}` : props.inputId)
}
</script>
