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
      <ModalHeader text="Name Your Cohort" />
      <hr />
      <form class="w-100 mb-2" @submit.prevent="createCohort" @keydown.esc="cancelModal">
        <div class="px-4 py-2">
          <v-text-field
            id="create-cohort-input"
            v-model="name"
            aria-label="Cohort name, 255 characters or fewer"
            aria-required="true"
            class="v-input-details-override mr-2"
            counter="255"
            density="compact"
            :disabled="isSaving"
            label="Cohort Name"
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
        <hr />
        <div class="d-flex justify-end px-4 py-2">
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
            class="ml-1"
            :disabled="isSaving"
            variant="plain"
            @click="cancelModal"
          >
            Cancel
          </v-btn>
        </div>
      </form>
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
