<template>
  <div>
    <form @submit.prevent="createCuratedGroup()" @keydown.esc="cancelModal">
      <div class="text-left ml-3 mr-3">
        <div>
          <label class="pb-2" for="create-input">Name:</label>
          <input
            id="create-input"
            v-model="name"
            class="cohort-create-input-name"
            type="text"
            maxlength="255"
            required>
        </div>
        <div class="faint-text mb-3">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
        <div id="create-error" v-if="error" class="has-error">{{ error }}</div>
        <div class="sr-only" aria-live="polite">{{ error }}</div>
        <div
          v-if="name.length === 255"
          class="sr-only"
          aria-live="polite">
          Curated group name cannot exceed 255 characters.
        </div>
      </div>
      <div class="modal-footer pl-0 mr-2">
        <b-btn
          id="create-confirm"
          :disabled="!name.length"
          @click.prevent="createCuratedGroup()"
          class="btn-primary-color-override"
          variant="primary">
          Save
        </b-btn>
        <b-btn
          id="create-cancel"
          @click="cancelModal()"
          variant="link">
          Cancel
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Validator from '@/mixins/Validator';

export default {
  name: 'CreateCuratedGroupModal',
  mixins: [Validator],
  props: {
    cancel: Function,
    create: Function
  },
  data: () => ({
    name: '',
    error: undefined
  }),
  watch: {
    name() {
      this.error = undefined;
    }
  },
  methods: {
    reset() {
      this.name = '';
      this.error = undefined;
    },
    cancelModal() {
      this.cancel();
      this.reset();
    },
    createCuratedGroup: function() {
      this.error = this.validateCohortName({ name: this.name });
      if (!this.error) {
        this.create(this.name);
        this.reset();
      }
    }
  }
};
</script>
