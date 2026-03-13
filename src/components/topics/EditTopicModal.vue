<template>
  <v-dialog
    v-model="showEditTopicModal"
    aria-labelledby="modal-header"
    class="modal-height-unset"
    :fullscreen="$vuetify.display.xs"
    persistent
  >
    <v-card
      class="modal-content"
      max-width="600"
      width="90vw"
    >
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader text="Create Topic" />
        </v-card-title>
        <v-card-text class="modal-body">
          <v-text-field
            id="create-topic-input"
            v-model="topic"
            :aria-describedby="`${errorMessage ? 'create-topic-input-error' : ''} create-topic-name-counter`"
            :aria-invalid="errorMessage"
            autocomplete="on"
            :disabled="isSaving"
            :error="!!errorMessage"
            :error-messages="errorMessage"
            label="Topic name"
            :maxlength="maxLabelLength"
            persistent-counter
            required
            :rules="[validate]"
            validate-on="lazy submit"
            variant="outlined"
            @keydown.enter="save"
            @update:model-value="resetValidation"
          >
            <template #counter="{max, value}">
              <CharacterCount :count="toInt(value)" id-prefix="create-topic-name" :max="toInt(max)" />
            </template>
            <template #message="{message}">
              <v-alert
                id="create-topic-input-error"
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
        <hr>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="topic-save"
            :action="save"
            :aria-disabled="!isValidLabel || isSaving || isLabelReserved"
            aria-label="Save Topic"
            :disabled="isSaving"
            :in-progress="isSaving"
            :text="isSaving ? 'Saving' : 'Save'"
          />
          <v-btn
            id="cancel"
            aria-label="Cancel Create Topic"
            class="ml-2"
            :disabled="isSaving"
            text="Cancel"
            variant="text"
            @click.stop="cancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import FocusLock from 'vue-focus-lock'
import {computed, onMounted, ref, watch} from 'vue'
import {find, trim} from 'lodash'
import CharacterCount from '@/components/util/CharacterCount'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {createTopic} from '@/api/topics'
import {putFocusNextTick, toInt, toggleModalBackgroundDisabled} from '@/lib/utils'

const props = defineProps({
  afterSave: {
    required: true,
    type: Function
  },
  allTopics: {
    required: true,
    type: Array
  },
  onCancel: {
    required: true,
    type: Function
  }
})

const errorMessage = ref('')
const isSaving = ref(false)
const maxLabelLength = 50
const minLabelLength = 3
const showEditTopicModal = ref(false)
const topic = ref(undefined)
const isLabelReserved = computed(() => {
  return !!find(props.allTopics, t => {
    const trimmed = trim(topic.value)
    return t.topic.toLowerCase() === trimmed.toLowerCase()
  })
})
const isValidLabel = computed(() => {
  return trim(topic.value).length >= minLabelLength
})

watch(showEditTopicModal, isOpen => {
  toggleModalBackgroundDisabled(isOpen)
  if (isOpen) {
    putFocusNextTick('create-topic-input')
  }
})

onMounted(() => {
  topic.value = ''
  showEditTopicModal.value = true
})

const cancel = () => {
  showEditTopicModal.value = false
  resetValidation()
  props.onCancel()
}

const resetValidation = () => {
  errorMessage.value = ''
}

const save = () => {
  if (validate() === true) {
    isSaving.value = true
    topic.value = trim(topic.value)
    createTopic(topic.value).then(data => {
      props.afterSave(data)
      isSaving.value = false
      showEditTopicModal.value = false
    })
  } else {
    putFocusNextTick('create-topic-input')
  }
}

const validate = () => {
  if (!isValidLabel.value) {
    errorMessage.value = `Label must be ${minLabelLength} or more characters.`
  } else if (isLabelReserved.value) {
    errorMessage.value = `Sorry, the label '${trim(topic.value)}' is assigned to an existing topic.`
  } else {
    resetValidation()
    return true
  }
}
</script>
