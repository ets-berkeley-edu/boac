<template>
  <v-dialog
    v-model="showModal"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card class="modal-content" min-width="600">
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader text="Name Your Degree Copy" />
        </v-card-title>
        <v-card-text class="modal-body">
          <label
            id="degree-name-input-label"
            for="degree-name-input"
          >
            Degree Name:
          </label>
          <v-text-field
            id="degree-name-input"
            v-model="name"
            :aria-describedby="`${errorMessage ? 'degree-name-input-error' : ''} degree-name-counter`"
            :aria-invalid="!!errorMessage"
            aria-labelledby="degree-name-input-label"
            autocomplete="on"
            class="mt-2"
            color="primary"
            density="comfortable"
            :disabled="isSaving"
            :error="!!errorMessage"
            :error-messages="errorMessage"
            maxlength="255"
            persistent-counter
            required
            :rules="[validate]"
            validate-on="lazy submit"
            @keydown.enter="createClone"
            @update:model-value="resetValidation"
          >
            <template #counter="{max, value}">
              <CharacterCount :count="toInt(value)" id-prefix="degree-name" :max="toInt(max)" />
            </template>
            <template #message="{message}">
              <v-alert
                id="degree-name-input-error"
                class="font-size-14 line-height-normal"
                density="compact"
                role="none"
                type="error"
                variant="tonal"
              >
                <span v-html="message" />
              </v-alert>
            </template>
          </v-text-field>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="clone-confirm"
            :action="createClone"
            :aria-disabled="!name.trim().length || isSaving || !!errorMessage || (templateToClone.name === name)"
            aria-label="Save Degree Copy"
            :disabled="isSaving"
            :in-progress="isSaving"
            :text="isSaving ? 'Saving' : 'Save Copy'"
          />
          <v-btn
            id="clone-cancel"
            aria-label="Cancel Copy Degree"
            class="ml-2"
            :disabled="isSaving"
            text="Cancel"
            variant="text"
            @click="cancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import {computed, onMounted, ref} from 'vue'
import {trim} from 'lodash'
import CharacterCount from '@/components/util/CharacterCount'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick, toInt} from '@/lib/utils'
import {cloneDegreeTemplate} from '@/api/degree'
import {validateDegreeTemplateName} from '@/lib/degree-progress'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  afterCreate: {
    required: true,
    type: Function
  },
  existingTemplates: {
    required: true,
    type: Array
  },
  templateToClone: {
    required: true,
    type: Object
  }
})

const errorMessage = ref('')
const isSaving = ref(false)
const name = ref(props.templateToClone.name)
const showModal = computed({
  get() {
    return !!props.templateToClone
  },
  set(value) {
    if (!value) {
      props.cancel()
    }
  }
})

onMounted(() => putFocusNextTick('degree-name-input'))

const createClone = () => {
  isSaving.value = true
  if (validate() === true) {
    alertScreenReader('Cloning template')
    cloneDegreeTemplate(props.templateToClone.id, trim(name.value)).then(data => {
      props.afterCreate(data)
      isSaving.value = false
    })
  } else {
    putFocusNextTick('degree-name-input')
    isSaving.value = false
  }
}

const resetValidation = () => {
  errorMessage.value = ''
}

const validate = () => {
  const validationReport = validateDegreeTemplateName(name.value, props.existingTemplates)
  errorMessage.value = validationReport.message
  return validationReport.valid || validationReport.message
}
</script>
