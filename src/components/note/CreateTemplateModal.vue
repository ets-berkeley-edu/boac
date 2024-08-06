<template>
  <v-dialog
    v-model="dialogModel"
    persistent
    width="100%"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <v-card-title>
        <ModalHeader text="Name Your Template" />
      </v-card-title>
      <hr />
      <form @submit.prevent="createTemplate">
        <div class="px-4 py-2">
          <v-text-field
            id="template-title-input"
            v-model="title"
            class="v-input-details-override"
            counter="255"
            density="compact"
            :disabled="isSaving"
            :error="!!error"
            label="Template name"
            maxlength="255"
            persistent-counter
            :rules="[validationRules.required, validationRules.maxLength]"
            variant="outlined"
          >
            <template #counter="{max, value}">
              <div id="name-template-counter" aria-live="polite" class="font-size-13 text-no-wrap my-1">
                <span class="sr-only">Template name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
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
        </div>
        <div class="d-flex justify-end px-4 py-2">
          <ProgressButton
            id="create-template-confirm"
            :action="createTemplate"
            :disabled="isSaving || !title.length || title.length > 255 || useNoteStore().boaSessionExpired"
            :in-progress="isSaving"
            :text="isSaving ? 'Saving' : 'Save'"
          />
          <v-btn
            id="cancel-template-create"
            class="ml-1"
            :disabled="isSaving"
            text="Cancel"
            variant="plain"
            @click="cancel"
          />
        </div>
      </form>
    </v-card>
  </v-dialog>
</template>

<script setup>
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
    putFocusNextTick('modal-header')
  } else {
    reset()
    props.onHidden()
  }
}
</script>
