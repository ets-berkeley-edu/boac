<template>
  <v-overlay
    v-model="showModalProxy"
    aria-label="Name Your Template"
    class="justify-center overflow-auto"
    persistent
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <ModalHeader text="Name Your Template" />
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
        <hr class="my-2" />
        <div class="d-flex justify-end px-4 py-2">
          <ProgressButton
            id="create-template-confirm"
            :action="createTemplate"
            :disabled="isSaving || !title.length || title.length > 255 || useNoteStore().boaSessionExpired"
            :in-progress="isSaving"
          >
            {{ isSaving ? 'Saving' : 'Save' }}
          </ProgressButton>
          <v-btn
            id="cancel-template-create"
            class="ml-1"
            :disabled="isSaving"
            variant="plain"
            @click="cancelModal"
          >
            Cancel
          </v-btn>
        </div>
      </form>
    </v-card>
  </v-overlay>
</template>

<script>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {useNoteStore} from '@/stores/note-edit-session'
import {validateTemplateTitle} from '@/lib/note'

export default {
  name: 'CreateTemplateModal',
  components: {ModalHeader, ProgressButton},
  props: {
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
    },
    showModal: {
      type: Boolean,
      required: true
    },
    toggleShow: {
      type: Function,
      required: true
    }
  },
  data: () => ({
    title: '',
    error: undefined,
    isSaving: false,
    validationRules: {
      required: value => !!value || 'Template name is required',
      maxLength: value => (!value || value.length <= 255) || 'Template name cannot exceed 255 characters.',
    }
  }),
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      },
      set(value) {
        this.toggleShow(value)
      }
    }
  },
  watch: {
    title() {
      this.error = undefined
    }
  },
  methods: {
    reset() {
      this.title = ''
      this.error = undefined
      this.isSaving = false
    },
    cancelModal() {
      this.cancel()
      this.reset()
    },
    createTemplate() {
      this.isSaving = true
      this.error = validateTemplateTitle({title: this.title})
      if (!this.error) {
        this.create(this.title)
      } else {
        this.isSaving = false
      }
    },
    onToggle(isOpen) {
      if (isOpen) {
        putFocusNextTick('modal-header')
      } else {
        this.onHidden()
      }
    },
    useNoteStore
  }
}
</script>
