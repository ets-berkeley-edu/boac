<template>
  <div>
    <form @submit.prevent="createCuratedGroup()">
      <div class="ml-3 mr-3">
        <div class="pb-2">Name:</div>
        <div>
          <input id="curated-group-create-input"
                 class="cohort-create-input-name"
                 v-model="name"
                 type="text"
                 maxlength="255"
                 required>
        </div>
        <div class="faint-text mb-3">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
        <div class="has-error" v-if="error">{{ error }}</div>
        <div class="sr-only" aria-live="polite">{{ error }}</div>
        <div class="sr-only"
             aria-live="polite"
             v-if="name.length === 255">Curated group name cannot exceed 255 characters.</div>
      </div>
      <div class="modal-footer pl-0 mr-2">
        <b-btn id="cohort-create-confirm"
               variant="primary"
               :disabled="!name.length"
               @click.prevent="createCuratedGroup()">
          Save
        </b-btn>
        <b-btn id="curated-cohort-create-cancel-btn"
               variant="link"
               @click="cancelModal()">Cancel</b-btn>
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
  },
  watch: {
    name() {
      this.error = undefined;
    }
  }
};
</script>
