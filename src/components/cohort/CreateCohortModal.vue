<template>
  <v-overlay
    v-model="showModalProxy"
    class="justify-center overflow-auto"
    persistent
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <ModalHeader clazz="px-4" text="Name Your Cohort" />
      <hr />
      <div class="px-8 w-100">
        <form @submit.prevent="createCohort" @keydown.esc="cancelModal">
          <div class="pt-2">
            <v-text-field
              id="create-cohort-input"
              v-model="name"
              aria-label="Cohort name, 255 characters or fewer"
              aria-required="true"
              class="v-input-details-override mr-2"
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
              @keyup.esc="cancel"
            >
              <template #counter="{max, value}">
                <div id="name-create-cohort-counter" aria-live="polite" class="font-size-13 text-no-wrap ml-2 mt-1">
                  <span class="sr-only">Cohort name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
                </div>
              </template>
            </v-text-field>
          </div>
          <div class="d-flex justify-end mt-4">
            <ProgressButton
              id="create-confirm"
              :action="createCohort"
              :disabled="!name.length"
              :in-progress="isSaving"
            >
              Save
            </ProgressButton>
            <v-btn
              id="create-cancel"
              :disabled="isSaving"
              variant="plain"
              @click="cancelModal"
            >
              Cancel
            </v-btn>
          </div>
        </form>
      </div>
    </v-card>
  </v-overlay>
</template>

<script>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
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
      this.cancel()
      this.reset()
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
    onToggle(isOpen) {
      if (isOpen) {
        putFocusNextTick('modal-header')
      } else {
        this.cancel()
      }
    },
    reset() {
      this.isSaving = false
      this.name = ''
    }
  }
}
</script>
