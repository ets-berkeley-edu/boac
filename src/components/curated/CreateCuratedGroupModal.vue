<template>
  <div>
    <form @submit.prevent="createCuratedGroup" @keydown.esc="cancelModal">
      <div class="text-left ml-3 mr-3">
        <label id="label-of-create-input" for="create-input"><span class="sr-only">Curated group </span>Name:</label>
        <b-form-input
          id="create-input"
          v-model="name"
          aria-labelledby="label-of-create-input"
          class="cohort-create-input-name"
          maxlength="255"
          size="lg"
        />
        <div class="faint-text mb-3">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
        <div
          v-if="error"
          id="create-error"
          class="has-error"
          aria-live="polite"
          role="alert"
        >
          {{ error }}
        </div>
        <div
          v-if="name.length === 255"
          class="sr-only"
          aria-live="polite"
        >
          Curated group name cannot exceed 255 characters.
        </div>
      </div>
      <div class="modal-footer mb-0 pb-0 pl-0 mr-2">
        <b-btn
          id="create-confirm"
          :disabled="!name.length"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="createCuratedGroup"
        >
          Save
        </b-btn>
        <b-btn
          id="create-cancel"
          variant="link"
          @click="cancelModal"
        >
          Cancel
        </b-btn>
      </div>
    </form>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Validator from '@/mixins/Validator'

export default {
  name: 'CreateCuratedGroupModal',
  mixins: [Context, Validator],
  props: {
    cancel: {
      required: true,
      type: Function
    },
    create: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    name: '',
    error: undefined
  }),
  watch: {
    name() {
      this.error = undefined
    }
  },
  methods: {
    reset() {
      this.name = ''
      this.error = undefined
    },
    cancelModal() {
      this.cancel()
      this.reset()
    },
    createCuratedGroup: function() {
      this.error = this.validateCohortName({ name: this.name })
      if (!this.error) {
        this.create(this.name)
        this.reset()
      }
    }
  }
}
</script>
