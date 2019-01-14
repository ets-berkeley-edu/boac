<template>
  <div>
    <form @submit.prevent="createCohort()">
      <div id="cohort-create-body">
        <div class="pb-2">Name:</div>
        <div>
          <input id="cohort-create-input"
                 ref="modalNameInput"
                 class="cohort-create-input-name"
                 v-model="name"
                 type="text"
                 maxlength="255"
                 autofocus
                 required>
        </div>
        <div class="faint-text">255 character limit <span v-if="name.length">({{255 - name.length}} left)</span></div>
        <div class="has-error" v-if="error">{{ error }}</div>
      </div>
      <div class="modal-footer">
        <b-btn id="cohort-create-confirm"
               variant="primary"
               :disabled="!name.length"
               @click.prevent="createCohort()">
          Save
        </b-btn>
        <b-btn type="button"
               id="cohort-create-cancel"
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
    createCohort: function() {
      let errorMessage = this.validateCohortName({ name: this.name });
      if (errorMessage) {
        this.error = errorMessage;
      } else {
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
