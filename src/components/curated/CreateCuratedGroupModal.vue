<template>
  <div>
    <form @submit="createCuratedGroup($event)">
      <div id="curated-cohort-create-body" class="modal-body">
        <div class="curated-cohort-create-form-name">Name:</div>
        <div>
          <input id="curated-cohort-create-input"
                 ref="modalNameInput"
                 class="curated-cohort-create-input-name"
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
        <b-btn id="curated-cohort-create-confirm-btn"
               variant="primary"
               :aria-disabled="!name.length"
               :disabled="!name.length"
               @click="createCuratedGroup($event)">
          Save
        </b-btn>
        <b-btn type="button"
               id="curated-cohort-create-cancel-btn"
               class="btn btn-default"
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
    createCuratedGroup: function(event) {
      event.preventDefault();
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
