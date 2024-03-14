<template>
  <v-overlay
    v-model="showModalProxy"
    aria-label="Rename Your Template"
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
      <ModalHeader text="Rename Your Template" />
      <hr />
      <form @submit.prevent="renameTemplate">
        <div class="px-4 py-2">
          <v-text-field
            id="rename-template-input"
            :model-value="title"
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
          >
            {{ isSaving ? 'Renaming' : 'Rename' }}
          </ProgressButton>
          <v-btn
            id="cancel-rename-template"
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
import {validateTemplateTitle} from '@/lib/note'

export default {
  name: 'RenameTemplateModal',
  components: {ModalHeader, ProgressButton},
  props: {
    cancel: {
      type: Function,
      required: true
    },
    rename: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    },
    template: {
      type: Object,
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
  mounted() {
    this.title = this.template.title
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
    onToggle(isOpen) {
      if (isOpen) {
        putFocusNextTick('modal-header')
      }
    },
    renameTemplate: function() {
      this.isSaving = true
      this.error = validateTemplateTitle({id: this.template.id, title: this.title})
      if (!this.error) {
        this.rename(this.title)
      } else {
        this.isSaving = false
      }
    }
  }
}
</script>
