<template>
  <b-modal
    id="create-note-template"
    v-model="showModalAlias"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header-close
    title="Name Your Template"
    @shown="focusModalById('create-input')">
    <div>
      <form @submit.prevent="createTemplate()">
        <div class="ml-3 mr-3">
          <div class="pb-2">Template name:</div>
          <div>
            <input
              id="template-title-input"
              v-model="title"
              class="cohort-create-input-name"
              type="text"
              maxlength="255"
              required>
          </div>
          <div class="faint-text mb-3"><span class="sr-only">Template name has a </span>255 character limit <span v-if="title.length">({{ 255 - title.length }} left)</span></div>
          <div v-if="error" id="create-error" class="has-error">{{ error }}</div>
          <div class="sr-only" aria-live="polite">{{ error }}</div>
          <div
            v-if="title.length === 255"
            class="sr-only"
            aria-live="polite">
            Template name cannot exceed 255 characters.
          </div>
        </div>
        <div class="modal-footer pl-0 mr-2">
          <b-btn
            id="create-template-confirm"
            class="btn-primary-color-override"
            variant="primary"
            :disabled="!title.length"
            @click.prevent="createTemplate()">
            Save
          </b-btn>
          <b-btn
            id="cancel-template-create"
            variant="link"
            @click="cancelModal()">
            Cancel
          </b-btn>
        </div>
      </form>
    </div>
  </b-modal>
</template>

<script>
import Util from '@/mixins/Util';
import Validator from '@/mixins/Validator';

export default {
  name: 'CreateTemplateModal',
  mixins: [Util, Validator],
  props: {
    cancel: Function,
    create: Function,
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    title: '',
    error: undefined,
    showModalAlias: undefined
  }),
  watch: {
    showModal(value) {
      this.showModalAlias = value;
    },
    title() {
      this.error = undefined;
    }
  },
  created() {
    this.showModalAlias = this.showModal;
  },
  methods: {
    reset() {
      this.title = '';
      this.error = undefined;
    },
    cancelModal() {
      this.cancel();
      this.reset();
    },
    createTemplate: function() {
      this.error = this.validateTemplateTitle({ title: this.title });
      if (!this.error) {
        this.create(this.title);
        this.reset();
      }
    }
  }
}
</script>
