<template>
  <v-overlay
    v-model="showModalProxy"
    aria-label="Name Your Template"
    body-class="pl-0 pr-0"
    @hidden="onHidden"
    @shown="putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader text="Name Your Template" />
      <form @submit.prevent="createTemplate">
        <div class="ml-3 mr-3">
          <div>
            <label class="pb-2" for="template-title-input">Template name:</label>
            <input
              id="template-title-input"
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
            id="create-error"
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
        <div class="modal-footer pl-0">
          <v-btn
            id="create-template-confirm"
            :disabled="!title.length"
            class="btn-primary-color-override"
            @click.prevent="createTemplate"
          >
            Save
          </v-btn>
          <v-btn
            id="cancel-template-create"
            class="pl-1"
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
import Util from '@/mixins/Util'
import ModalHeader from '@/components/util/ModalHeader'
import {validateTemplateTitle} from '@/lib/note'

export default {
  name: 'CreateTemplateModal',
  components: {ModalHeader},
  mixins: [Util],
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
  methods: {
    reset() {
      this.title = ''
      this.error = undefined
    },
    cancelModal() {
      this.cancel()
      this.reset()
    },
    createTemplate: function() {
      this.error = validateTemplateTitle({title: this.title})
      if (!this.error) {
        this.create(this.title)
        this.reset()
      }
    }
  }
}
</script>
