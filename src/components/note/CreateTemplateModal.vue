<template>
  <v-dialog
    v-model="dialogModel"
    aria-labelledby="modal-header"
    class="modal-height-unset"
    :fullscreen="$vuetify.display.xs"
    persistent
  >
    <v-card
      class="modal-content"
      max-width="700"
      width="90vw"
    >
      <v-card-title>
        <ModalHeader text="Name Your Template" />
      </v-card-title>
      <v-card-text class="modal-body">
        <v-text-field
          id="template-title-input"
          v-model="title"
          :aria-describedby="`${error ? 'template-title-error' : ''} template-name-counter`"
          :aria-invalid="!!error"
          autocomplete="on"
          class="my-3"
          density="compact"
          :disabled="isSaving"
          :error="!!error"
          :error-messages="error"
          label="Template name"
          maxlength="255"
          persistent-counter
          required
          :rules="[validationRules.required, validationRules.maxLength]"
          validate-on="lazy submit"
          variant="outlined"
          @keydown.stop.prevent.esc="cancel"
          @keydown.enter="createTemplate"
        >
          <template #counter="{max, value}">
            <CharacterCount :count="toInt(value)" id-prefix="template-name" :max="toInt(max)" />
          </template>
          <template #message="{message}">
            <v-alert
              id="template-title-error"
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
      <v-card-actions class="modal-footer">
        <ProgressButton
          id="create-template-confirm"
          :action="createTemplate"
          :aria-disabled="error || isSaving || useNoteStore().boaSessionExpired"
          aria-label="Save Template"
          class="mr-2"
          :disabled="isSaving || useNoteStore().boaSessionExpired"
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
    </v-card>
  </v-dialog>
</template>

<script setup>
import {ref, watch} from 'vue'
import {trim} from 'lodash'
import CharacterCount from '@/components/util/CharacterCount'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick, toInt} from '@/lib/utils'
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
  required: value => !!trim(value) || 'Template name is required',
  maxLength: value => (!value || trim(value).length <= 255) || 'Template name cannot exceed 255 characters.',
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
    putFocusNextTick('template-title-input')
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
