<template>
  <v-dialog
    v-model="showModalProxy"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <FocusLock @keydown.esc="cancelModal">
        <v-card-title>
          <ModalHeader text="Name Your Cohort" />
        </v-card-title>
        <form @submit.prevent="createCohort">
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
              :rules="[validate]"
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
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {alertScreenReader, putFocusNextTick} from '@/lib/utils'
import {validateCohortName} from '@/lib/cohort'
import {computed, ref, watch} from 'vue'

const props = defineProps({
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
})

const isInvalid = ref(true)
const isSaving = ref(false)
const name = ref('')

const showModalProxy = computed(() => {
  return props.showModal
})

watch(showModalProxy, isOpen => {
  if (isOpen) {
    putFocusNextTick('create-cohort-input')
  } else {
    props.cancel()
  }
})

const cancelModal = () => {
  alertScreenReader('Canceled')
  props.cancel()
  reset()
  putFocusNextTick('save-cohort-button')
}

const createCohort = () => {
  if (true !== validateCohortName({name: name.value})) {
    putFocusNextTick('create-cohort-input')
  } else {
    isSaving.value = true
    props.create(name.value).then(reset)
  }
}

const reset = () => {
  isSaving.value = false
  name.value = ''
}

const validate = name => {
  const valid = validateCohortName({name})
  isInvalid.value = true !== valid
  return valid
}
</script>
