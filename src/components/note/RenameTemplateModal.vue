<template>
  <v-overlay
    v-model="showModalProxy"
    aria-label="Rename Your Template"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @shown="putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader text="Rename Your Template" />
      <form @submit.prevent="renameTemplate">
        <div class="ml-3 mr-3">
          <div>
            <label for="rename-template-input" class="pb-2">Template name:</label>
            <input
              id="rename-template-input"
              v-model="title"
              class="cohort-create-input-name"
              type="text"
              maxlength="255"
              required
            >
          </div>
          <div class="faint-text mb-3"><span class="sr-only">Template name has a </span>255 character limit <span v-if="title.length">({{ 255 - title.length }} left)</span></div>
          <div
            v-if="error"
            id="rename-template-error"
            aria-live="polite"
            role="alert"
            class="has-error"
          >
            {{ error }}
          </div>
          <div
            v-if="title.length === 255"
            class="sr-only"
            aria-live="polite"
          >
            Template name cannot exceed 255 characters.
          </div>
        </div>
        <div class="modal-footer pl-0 mr-2">
          <v-btn
            id="rename-template-confirm"
            :disabled="!title.length"
            class="btn-primary-color-override"
            @click.prevent="renameTemplate"
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
    </div>
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
    error: undefined
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
      this.error = validateTemplateTitle({id: this.template.id, title: this.title})
      if (!this.error) {
        this.rename(this.title)
      }
    }
  }
}
</script>
