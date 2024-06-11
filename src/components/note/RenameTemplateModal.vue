<template>
  <v-dialog
    v-model="dialog"
    aria-label="Rename Your Template"
    class="justify-center overflow-auto"
    persistent
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card width="600">
      <ModalHeader header-id="rename-template-modal-header" text="Rename Your Template" />
      <hr />
      <form @submit.prevent="renameTemplate">
        <div class="px-4 py-2">
          <v-text-field
            id="rename-template-input"
            v-model="title"
            class="v-input-details-override"
            counter="255"
            density="compact"
            :disabled="isSaving"
            label="Template name"
            maxlength="255"
            persistent-counter
            :rules="[
              v => !!v || 'Template name is required',
              v => !v || v.length <= 255 || 'Template name cannot exceed 255 characters.'
            ]"
            variant="outlined"
          >
            <template #counter="{max, value}">
              <div id="rename-template-counter" aria-live="polite" class="font-size-13 text-no-wrap my-1">
                <span class="sr-only">Template name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
              </div>
            </template>
          </v-text-field>
          <div
            v-if="error"
            id="rename-template-error"
            aria-live="polite"
            class="text-error font-size-13 font-weight-regular"
            role="alert"
          >
            {{ error }}
          </div>
        </div>
        <hr class="my-2" />
        <div class="d-flex justify-end px-4 py-2">
          <ProgressButton
            id="rename-template-confirm"
            :action="renameTemplate"
            :disabled="isSaving || !title.length || title.length > 255"
            :in-progress="isSaving"
            :text="isSaving ? 'Renaming' : 'Rename'"
          />
          <v-btn
            id="cancel-rename-template"
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
import {validateTemplateTitle} from '@/lib/note'
import {watch} from 'vue'

const props = defineProps({
  cancel: {
    type: Function,
    required: true
  },
  rename: {
    type: Function,
    required: true
  },
  template: {
    type: Object,
    required: true
  }
})

let title = props.template.title
let error = undefined
let isSaving = false

// eslint-disable-next-line vue/require-prop-types
const dialog = defineModel()

watch(title, () => error = undefined)

putFocusNextTick('rename-template-modal-header')

const renameTemplate = () => {
  isSaving = true
  error = validateTemplateTitle({id: props.template.id, title: title})
  if (error) {
    isSaving = false
  } else {
    props.rename(title)
  }
}
</script>
