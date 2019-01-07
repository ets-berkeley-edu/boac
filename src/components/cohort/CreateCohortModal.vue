<template>
  <div>
    <form @submit.prevent="createCohort()">
      <div id="cohort-create-body" class="modal-body">
        <div class="cohort-create-form-name">Name:</div>
        <div>
          <input id="cohort-create-input"
                 ref="modalNameInput"
                 class="cohort-create-input-name"
                 @change="error.hide = true"
                 v-model="name"
                 type="text"
                 maxlength="255"
                 autofocus
                 required>
        </div>
        <div class="faint-text">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
        <div class="has-error" v-if="error.message && !error.hide">{{ error.message }}</div>
      </div>
      <div class="modal-footer">
        <b-btn id="cohort-create-confirm-btn"
               variant="primary"
               :disabled="!name.length"
               @click.prevent="createCohort()">
          Save
        </b-btn>
        <b-btn type="button"
               id="cohort-create-cancel-btn"
               class="btn btn-default"
               @click="cancelModal()">Cancel</b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Validator from '@/mixins/Validator';

export default {
  name: 'CreateCohortModal',
  mixins: [Validator],
  props: {
    cancel: Function,
    create: Function
  },
  data: () => ({
    name: '',
    error: {
      message: null,
      hide: false
    }
  }),
  methods: {
    reset() {
      this.name = '';
      this.error = { message: null, hide: false };
    },
    cancelModal() {
      this.cancel();
      this.reset();
    },
    createCohort: function() {
      let errorMessage = this.validateCohortName({ name: this.name });
      if (errorMessage) {
        this.error = { message: errorMessage, hide: false };
      } else {
        this.create(this.name);
        this.reset();
      }
    }
  }
};
</script>
