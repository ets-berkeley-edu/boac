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
      width="100%"
    >
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader :text="`Name Your ${describeCuratedGroupDomain(domain, true)}`" />
        </v-card-title>
        <v-card-text class="modal-body">
          <v-text-field
            id="create-curated-group-input"
            ref="groupNameInput"
            v-model="name"
            aria-describedby="create-curated-group-input-details"
            :aria-invalid="!!errorMessage"
            autocomplete="on"
            counter="255"
            :disabled="isSaving"
            :error="!!errorMessage"
            :error-messages="errorMessage"
            :label="`${describeCuratedGroupDomain(domain, true)} Name`"
            maxlength="255"
            persistent-counter
            required
            :rules="[validate]"
            validate-on="lazy submit"
            @keydown.enter="createCuratedGroup"
            @update:model-value="resetValidation"
          >
            <template #counter="{max, value}">
              <CharacterCount :count="toInt(value)" id-prefix="create-curated-group-name" :max="toInt(max)" />
            </template>
            <template #message="{message}">
              <v-alert
                id="create-curated-group-name-error"
                class="font-size-14 line-height-normal"
                density="compact"
                role="none"
                :text="message"
                type="error"
                variant="tonal"
              />
            </template>
          </v-text-field>
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="create-curated-group-confirm"
            :action="createCuratedGroup"
            :aria-disabled="isEmpty(name) || isInvalid"
            aria-label="Save Curated Group"
            :disabled="isSaving"
            :in-progress="isSaving"
            text="Save"
          />
          <v-btn
            id="create-curated-group-cancel"
            aria-label="Cancel Create Curated Group"
            :disabled="isSaving"
            text="Cancel"
            variant="text"
            @click="cancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {isEmpty} from 'lodash'
import FocusLock from 'vue-focus-lock'
import {computed, ref, watch} from 'vue'
import CharacterCount from '@/components/util/CharacterCount'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {describeCuratedGroupDomain} from '@/lib/berkeley-utils'
import {putFocusNextTick, toInt} from '@/lib/utils'
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

const errorMessage = ref('')
const groupNameInput = ref(null)
const isInvalid = ref(false)
const name = ref('')

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
  reset()
}

const createCuratedGroup = () => {
  if (validate(name.value) !== true) {
    putFocusNextTick('create-curated-group-input')
  } else {
    props.create(name.value)
  }
}

const reset = () => {
  name.value = ''
  resetValidation()
}

const resetValidation = () => {
  errorMessage.value = ''
  isInvalid.value = false
  groupNameInput.value?.resetValidation?.()
}

const validate = name => {
  const result = validateCohortName({name})
  if (result === true) {
    resetValidation()
  } else {
    errorMessage.value = result
    isInvalid.value = true
  }
  return result
}
</script>
