<template>
  <v-dialog
    v-model="showModalProxy"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
      width="100%"
    >
      <FocusLock @keydown.esc="cancelModal">
        <v-card-title>
          <ModalHeader text="Name Your Cohort" />
        </v-card-title>
        <form @submit.prevent="createCohort">
          <v-card-text class="modal-body">
            <v-text-field
              id="create-cohort-input"
              ref="cohortNameInput"
              v-model="name"
              aria-describedby="create-cohort-input-messages"
              :aria-invalid="!!errorMessage"
              autocomplete="on"
              counter="255"
              :disabled="isSaving"
              :error="!!errorMessage"
              :error-messages="errorMessage"
              label="Cohort name"
              maxlength="255"
              persistent-counter
              required
              :rules="[validate]"
              validate-on="lazy invalid-input"
              @keyup.esc="cancelModal"
            >
              <template #counter="{max, value}">
                <CharacterCount :count="toInt(value)" id-prefix="create-cohort-name" :max="toInt(max)" />
              </template>
              <template #message="{message}">
                <v-alert
                  id="create-cohort-name-error"
                  class="font-size-14 line-height-normal"
                  density="compact"
                  role="none"
                  :text="message"
                  type="error"
                  variant="tonal"
                />
              </template>
            </v-text-field>
          </v-card-text>
          <v-card-actions class="modal-footer py-0">
            <ProgressButton
              id="create-cohort-confirm-btn"
              :action="createCohort"
              :aria-disabled="isEmpty(name) || isInvalid"
              aria-label="Save Cohort"
              :disabled="isSaving"
              :in-progress="isSaving"
              text="Save"
            />
            <v-btn
              id="create-cohort-cancel-btn"
              aria-label="Cancel Save Cohort"
              :disabled="isSaving"
              text="Cancel"
              variant="text"
              @click="cancelModal"
            />
          </v-card-actions>
        </form>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {isEmpty} from 'lodash'
import FocusLock from 'vue-focus-lock'
import {computed, ref, watch} from 'vue'
import CharacterCount from '@/components/util/CharacterCount'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {validateCohortName} from '@/lib/cohort'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  create: {
    required: true,
    type: Function
  },
  showModal: {
    required: true,
    type: Boolean
  }
})

const cohortNameInput = ref()
const errorMessage = ref('')
const isInvalid = ref(true)
const isSaving = ref(false)
const name = ref('')

const showModalProxy = computed(() => {
  return props.showModal
})

watch(showModalProxy, isOpen => {
  if (isOpen) {
    putFocusNextTick('create-cohort-input')
  } else {
    props.cancel()
  }
})

const cancelModal = () => {
  alertScreenReader('Canceled save cohort')
  cohortNameInput.value.resetValidation()
  reset()
  props.cancel()
  putFocusNextTick('save-cohort-button')
}

const createCohort = () => {
  if (true !== validate(name.value)) {
    putFocusNextTick('create-cohort-input')
  } else {
    isSaving.value = true
    props.create(name.value).then(reset)
  }
}

const reset = () => {
  isSaving.value = false
  name.value = ''
  errorMessage.value = ''
  isInvalid.value = false
}

const validate = name => {
  const result = validateCohortName({name})
  if (result === true) {
    errorMessage.value = ''
    isInvalid.value = false
  } else {
    errorMessage.value = result
    isInvalid.value = true
  }
  return result
}
</script>
