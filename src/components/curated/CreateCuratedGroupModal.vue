<template>
  <div>
    <ModalHeader :text="`Name Your ${domainLabel(true)}`" />
    <form @submit.prevent="createCuratedGroup" @keydown.esc="cancelModal">
      <div class="m-3">
        <label id="label-of-create-input" for="create-input" tabindex="-1"><span class="sr-only">{{ domainLabel(true) }} </span>Name:</label>
        <b-form-input
          id="create-input"
          v-model="name"
          aria-labelledby="label-of-create-input"
          class="cohort-create-input-name"
          maxlength="255"
          size="lg"
        />
        <div class="faint-text my-3">255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></div>
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
          {{ _capitalize(domainLabel(false)) }} name cannot exceed 255 characters.
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
import ModalHeader from '@/components/util/ModalHeader'
import Util from '@/mixins/Util'
import Validator from '@/mixins/Validator'
import {describeCuratedGroupDomain} from '@/berkeley'

export default {
  name: 'CreateCuratedGroupModal',
  mixins: [Context, Util, Validator],
  components: {ModalHeader},
  props: {
    cancel: {
      required: true,
      type: Function
    },
    create: {
      required: true,
      type: Function
    },
    domain: {
      required: true,
      type: String
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
    cancelModal() {
      this.cancel()
      this.reset()
    },
    createCuratedGroup: function() {
      this.error = this.validateCohortName({name: this.name})
      if (!this.error) {
        this.create(this.name)
        this.reset()
      }
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    reset() {
      this.name = ''
      this.error = undefined
    }
  }
}
</script>
