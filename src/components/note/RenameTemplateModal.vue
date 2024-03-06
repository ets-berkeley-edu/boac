<template>
  <v-overlay
    v-model="showModalProxy"
    aria-label="Rename Your Template"
    class="justify-center overflow-auto"
    max-width="900"
    min-width="400"
    persistent
    width="80%"
    @shown="putFocusNextTick('modal-header')"
  >
    <v-card class="modal-content">
      <ModalHeader text="Rename Your Template" />
      <hr />
      <form @submit.prevent="renameTemplate">
        <div class="px-4 py-2">
          <v-text-field
            id="rename-template-input"
            v-model="title"
            class="rename-template-input"
            counter="255"
            density="compact"
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
          <v-btn
            id="rename-template-confirm"
            color="primary"
            :disabled="isSaving || !title.length || title.length > 255"
            @click.prevent.once="renameTemplate"
          >
            Rename
          </v-btn>
          <v-btn
            id="cancel-rename-template"
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
import Util from '@/mixins/Util'
import {validateTemplateTitle} from '@/lib/note'

export default {
  name: 'RenameTemplateModal',
  components: {ModalHeader},
  mixins: [Util],
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
    cancelModal() {
      this.error = undefined
      this.cancel()
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

<style lang="scss">
.rename-template-input {
  .v-input__details {
    align-items: baseline;
    flex-wrap: wrap;
    padding: 6px 10px 0 10px;
    .v-counter {
      flex-grow: 1;
      flex-shrink: 0;
      text-align: end;
    }
    .v-messages {
      font-size: 14px;
      min-height: unset;
      .v-messages__message {
        margin: 4px 0;
      }
    }
  }
}
</style>
