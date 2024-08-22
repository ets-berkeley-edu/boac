<template>
  <v-dialog
    v-model="showModalProxy"
    aria-labelledby="modal-header"
    persistent
  >
    <FocusLock>
      <v-card
        class="modal-content"
        min-width="400"
        max-width="600"
      >
        <v-card-title>
          <ModalHeader text="Name Your Cohort" />
        </v-card-title>
        <form @submit.prevent="createCohort" @keydown.esc="cancelModal">
          <v-card-text class="modal-body">
            <v-text-field
              id="create-cohort-input"
              v-model="name"
              aria-label="Cohort name, 255 characters or fewer"
              aria-required="true"
              class="v-input-details-override"
              counter="255"
              density="compact"
              :disabled="isSaving"
              maxlength="255"
              required
              type="text"
              persistent-counter
              :rules="[validationRules.valid]"
              validate-on="lazy input"
              variant="outlined"
              @keyup.esc="cancelModal"
            >
              <template #counter="{max, value}">
                <div id="name-create-cohort-counter" aria-live="polite" class="font-size-13 text-no-wrap ml-2 mt-1">
                  <span class="sr-only">Cohort name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
                </div>
              </template>
            </v-text-field>
          </v-card-text>
          <hr />
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="create-cohort-confirm-btn"
              :action="createCohort"
              :disabled="!name.length || isInvalid"
              :in-progress="isSaving"
              text="Save"
            />
            <v-btn
              id="create-cohort-cancel-btn"
              class="ml-2"
              :disabled="isSaving"
              variant="text"
              @click="cancelModal"
            >
              Cancel
            </v-btn>
          </v-card-actions>
        </form>
      </v-card>
    </FocusLock>
  </v-dialog>
</template>

<script>
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {validateCohortName} from '@/lib/cohort'

export default {
  name: 'CreateCohortModal',
  components: {ModalHeader, ProgressButton},
  props: {
    cancel: {
      required: true,
      type: Function
    },
    create: {
      required: true,
      type: Function
    },
    showModal: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    isInvalid: true,
    isSaving: false,
    name: '',
    validationRules: {}
  }),
  computed: {
    showModalProxy() {
      return this.showModal
    }
  },
  watch: {
    showModalProxy(isOpen) {
      if (isOpen) {
        putFocusNextTick('create-cohort-input')
      } else {
        this.cancel()
      }
    }
  },
  created() {
    this.validationRules = {
      valid: name => {
        const valid = validateCohortName({name})
        this.isInvalid = true !== valid
        return valid
      }
    }
  },
  methods: {
    cancelModal() {
      alertScreenReader('Canceled')
      this.cancel()
      this.reset()
      putFocusNextTick('save-cohort-button')
    },
    createCohort() {
      if (true !== validateCohortName({name: this.name})) {
        putFocusNextTick('create-cohort-input')
      } else {
        this.isSaving = true
        this.create(this.name).then(() => {
          this.reset()
        })
      }
    },
    reset() {
      this.isSaving = false
      this.name = ''
    }
  }
}
</script>
