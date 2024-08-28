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
          <ModalHeader :text="`Name Your ${describeCuratedGroupDomain(domain, true)}`" />
        </v-card-title>
        <form @submit.prevent="createCuratedGroup">
          <v-card-text class="modal-body">
            <v-text-field
              id="create-curated-group-input"
              v-model="name"
              :aria-label="`${describeCuratedGroupDomain(domain, true)} name, 255 characters or fewer`"
              aria-required="true"
              class="v-input-details-override"
              counter="255"
              :disabled="isSaving"
              label="Name"
              maxlength="255"
              persistent-counter
              :required="!isSaving"
              :rules="[validate]"
              type="text"
              validate-on="lazy input"
              @keyup.esc="cancel"
            >
              <template #counter="{max, value}">
                <div id="name-create-cohort-counter" aria-live="polite" class="font-size-13 text-no-wrap ml-2 mt-1">
                  <span class="sr-only">{{ describeCuratedGroupDomain(domain, true) }} name has a </span>{{ max }} character limit <span v-if="value">({{ max - value }} left)</span>
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
              :disabled="isSaving"
              text="Cancel"
              variant="text"
              @click="cancelModal"
            />
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
import {computed, ref, watch} from 'vue'
import {describeCuratedGroupDomain} from '@/berkeley'
import {putFocusNextTick} from '@/lib/utils'
import {validateCohortName} from '@/lib/cohort'

const props = defineProps({
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
  isSaving: {
    required: false,
    type: Boolean
  },
  showModal: {
    required: true,
    type: Boolean
  }
})

const name = ref('')
const isInvalid = ref(false)

const showModalProxy = computed(() => {
  return props.showModal
})

watch(showModalProxy, isOpen => {
  if (isOpen) {
    putFocusNextTick('create-curated-group-input')
  } else {
    cancelModal()
  }
})

const cancelModal = () => {
  props.cancel()
  name.value = ''
}

const createCuratedGroup = () => {
  if (true !== validateCohortName({name: name.value})) {
    putFocusNextTick('create-cohort-input')
  } else {
    props.create(name.value)
  }
}

const validate = name => {
  const isValid = validateCohortName({name})
  isInvalid.value = true !== isValid
  return isValid
}
</script>
