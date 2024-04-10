<template>
  <b-modal
    v-model="showModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="cancel"
    @hide.prevent="cancel"
    @shown="putFocusNextTick('modal-header')"
  >
    <ModalHeader text="Name Your Degree Copy" />
    <form @submit.prevent="createClone" @keydown.esc="cancel">
      <div class="ma-3">
        <label id="degree-name-input-label" for="degree-name-input">Degree Name:</label>
        <b-form-input
          id="degree-name-input"
          v-model="name"
          aria-labelledby="degree-name-input-label"
          class="name-input"
          :disabled="isSaving"
          maxlength="255"
          size="lg"
          @keypress.enter.prevent="() => name.length && createClone()"
          @keyup.esc="cancel"
        />
        <div class="pl-2 pt-1">
          <span class="text-grey font-size-12"><span class="sr-only">Degree name has a </span>255 character limit <span v-if="name.length">({{ 255 - name.length }} left)</span></span>
          <span
            v-if="name.length === 255"
            aria-live="polite"
            class="sr-only"
            role="alert"
          >
            Degree name cannot exceed 255 characters.
          </span>
        </div>
        <div v-if="error" class="error-message-container mt-2 p-3">
          <span v-html="error"></span>
        </div>
      </div>
      <div class="modal-footer mb-0 mr-2 pb-0 pl-0">
        <b-btn
          id="clone-confirm"
          :disabled="!name.trim().length || isSaving || !!error || (templateToClone.name === name)"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="createClone"
        >
          <span v-if="isSaving"><v-progress-circular class="mr-1" size="small" /> Saving</span>
          <span v-if="!isSaving">Save Copy</span>
        </b-btn>
        <b-btn
          id="clone-cancel"
          :disabled="isSaving"
          variant="link"
          @click="cancel"
        >
          Cancel
        </b-btn>
      </div>
    </form>
  </b-modal>
</template>

<script>
import Context from '@/mixins/Context.vue'
import ModalHeader from '@/components/util/ModalHeader.vue'
import Util from '@/mixins/Util.vue'
import {cloneDegreeTemplate, getDegreeTemplates} from '@/api/degree'

export default {
  name: 'CloneTemplateModal',
  components: {ModalHeader},
  mixins: [Context, Util],
  props: {
    cancel: {
      required: true,
      type: Function
    },
    afterCreate: {
      required: true,
      type: Function
    },
    templateToClone: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    error: undefined,
    isSaving: false,
    name: ''
  }),
  computed: {
    showModal: {
      get() {
        return !!this.templateToClone
      },
      set(value) {
        if (!value) {
          this.cancel()
        }
      }
    }
  },
  watch: {
    name() {
      this.error = null
    }
  },
  created() {
    this.name = this.templateToClone.name
  },
  methods: {
    createClone() {
      this.isSaving = true
      getDegreeTemplates().then(data => {
        const lower = this.name.trim().toLowerCase()
        if (this._map(data, 'name').findIndex(s => s.toLowerCase() === lower) === -1) {
          this.alertScreenReader('Cloning template')
          cloneDegreeTemplate(this.templateToClone.id, this.name).then(data => {
            this.afterCreate(data)
            this.isSaving = false
          })
        } else {
          this.error = `A degree named <span class="font-weight-500">${this.name}</span> already exists. Please choose a different name.`
          this.alertScreenReader(this.error)
          this.isSaving = false
        }
      })
    }
  }
}
</script>

<style scoped>
.name-input {
  border: 1px solid #66afe9;
  border-radius: 4px;
  box-sizing: border-box;
}
</style>
