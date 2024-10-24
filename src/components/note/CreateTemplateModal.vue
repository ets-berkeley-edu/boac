<template>
  <v-dialog
    v-model="dialogModel"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <FocusLock>
        <v-card-title>
          <ModalHeader text="Name Your Template" />
        </v-card-title>
        <hr />
        <form @submit.prevent="createTemplate">
          <v-card-text class="modal-body">
            <v-text-field
              id="template-title-input"
              v-model="title"
              aria-label="Template name"
              class="v-input-details-override"
              counter="255"
              density="compact"
              :disabled="isSaving"
              :error="!!error"
              label="Template name"
              maxlength="255"
              persistent-counter
              :rules="[validationRules.required, validationRules.maxLength]"
              validate-on="blur lazy"
              variant="outlined"
            >
              <template #counter="{max, value}">
                <div id="name-template-counter" class="font-size-13 text-no-wrap my-1">
                  <span class="sr-only">Template name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
                  <span
                    v-if="value === 255"
                    aria-live="polite"
                    class="sr-only"
                    role="alert"
                  >
                    Template name cannot exceed 255 characters.
                  </span>
                </div>
              </template>
            </v-text-field>
            <div
              v-if="error"
              id="create-template-error"
              aria-live="polite"
              class="text-error font-size-13 font-weight-regular"
              role="alert"
            >
              {{ error }}
            </div>
          </v-card-text>
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="create-template-confirm"
              :action="createTemplate"
              aria-label="Save Template"
              class="mr-1"
              :disabled="isSaving || !title.length || title.length > 255 || useNoteStore().boaSessionExpired"
              :in-progress="isSaving"
              :text="isSaving ? 'Saving' : 'Save'"
            />
            <v-btn
              id="cancel-template-create"
              aria-label="Cancel Create Template"
              :disabled="isSaving"
              text="Cancel"
              variant="text"
              @click="cancel"
            />
          </v-card-actions>
        </form>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {ref, watch} from 'vue'
import {trim} from 'lodash'
import {useNoteStore} from '@/stores/note-edit-session'
import {validateTemplateTitle} from '@/lib/note'

const props = defineProps({
  cancel: {
    type: Function,
    required: true
  },
  create: {
    type: Function,
    required: true
  },
  onHidden: {
    type: Function,
    required: true
  }
})

const dialogModel = defineModel({type: Boolean})
const title = ref('')
const error = ref(undefined)
const isSaving = ref(false)
const validationRules = ref({
  required: value => !!value || 'Template name is required',
  maxLength: value => (!value || value.length <= 255) || 'Template name cannot exceed 255 characters.',
})

watch(dialogModel, () => {
  onToggle(dialogModel.value)
})

watch(title, () => {
  error.value = undefined
})

const reset = () => {
  title.value = ''
  error.value = undefined
  isSaving.value = false
}

const createTemplate = () => {
  isSaving.value = true
  const templateTitle = trim(title.value)
  error.value = validateTemplateTitle({title: templateTitle})
  if (!error.value) {
    props.create(templateTitle)
  } else {
    isSaving.value = false
  }
}

const onToggle = isOpen => {
  if (isOpen) {
    putFocusNextTick('template-title-input')
  } else {
    reset()
    props.onHidden()
  }
}
</script>
