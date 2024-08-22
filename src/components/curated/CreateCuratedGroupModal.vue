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
          <ModalHeader :text="`Name Your ${domainLabel(true)}`" />
        </v-card-title>
        <form @submit.prevent="createCuratedGroup" @keydown.esc="cancelModal">
          <v-card-text class="modal-body">
            <v-text-field
              id="create-curated-group-input"
              v-model="name"
              :aria-label="`${domainLabel(true)} name, 255 characters or fewer`"
              aria-required="true"
              class="v-input-details-override"
              counter="255"
              density="compact"
              :disabled="isSaving"
              label="Name"
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
                  <span class="sr-only">{{ domainLabel(true) }} name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
                </div>
              </template>
            </v-text-field>
          </v-card-text>
          <hr />
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="create-curated-group-confirm"
              :action="createCuratedGroup"
              :disabled="isSaving || !name.length || isInvalid"
              :in-progress="isSaving"
              text="Save"
            />
            <v-btn
              id="create-curated-group-cancel"
              class="ml-2"
              :disabled="isSaving"
              text="Cancel"
              variant="text"
              @click="cancelModal"
            />
          </v-card-actions>
        </form>
      </v-card>
    </FocusLock>
  </v-dialog>
</template>

<script>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {describeCuratedGroupDomain} from '@/berkeley'
import {validateCohortName} from '@/lib/cohort'

export default {
  name: 'CreateCuratedGroupModal',
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
    domain: {
      required: true,
      type: String
    },
    showModal: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    name: '',
    isInvalid: false,
    isSaving: false,
    validationRules: {}
  }),
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      }
    }
  },
  watch: {
    showModalProxy(isOpen) {
      if (isOpen) {
        putFocusNextTick('create-curated-group-input')
      } else {
        this.cancelModal()
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
      this.cancel()
      this.reset()
    },
    createCuratedGroup: function() {
      if (true !== validateCohortName({name: this.name})) {
        putFocusNextTick('create-cohort-input')
      } else {
        this.isSaving = true
        this.create(this.name).then(() => {
          this.reset()
        })
      }
    },
    domainLabel(capitalize) {
      return describeCuratedGroupDomain(this.domain, capitalize)
    },
    reset() {
      this.isSaving = false
      this.name = ''
    }
  }
}
</script>
