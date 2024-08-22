<template>
  <v-dialog
    v-model="showEditTopicModal"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card
      class="modal-content"
      min-width="400"
    >
      <FocusLock>
        <v-card-title>
          <ModalHeader text="Create Topic" />
        </v-card-title>
        <form @submit.prevent="save">
          <v-card-text class="modal-body">
            <div class="text-field-width d-block">
              <v-text-field
                id="create-topic-input"
                v-model="topic"
                aria-describedby="input-live-help topic-label-error"
                hide-details
                required
                :maxlength="50"
                variant="outlined"
              >
              </v-text-field>
            </div>
            <div id="topic-label-error" class="font-size-14 mt-0 pl-2 pt-2">
              <span v-if="!isValidLabel">Label must be {{ minLabelLength }} or more characters.</span>
              <span v-if="isLabelReserved">Sorry, the label '{{ trim(topic) }}' is assigned to an existing topic.</span>
            </div>
            <div class="text-grey font-size-14 pl-2 pt-2">
              <span v-if="!isLabelReserved && isValidLabel" id="input-live-help">
                {{ maxLabelLength }} character limit <span v-if="topic.length">({{ maxLabelLength - topic.length }} left)</span>
              </span>
            </div>
          </v-card-text>
          <hr />
          <v-card-actions class="modal-footer">
            <ProgressButton
              id="topic-save"
              :action="save"
              :disabled="disableSaveButton"
              :in-progress="isSaving"
              :text="isSaving ? 'Saving' : 'Save'"
            />
            <v-btn
              id="cancel"
              class="ml-2"
              :disabled="isSaving"
              variant="text"
              @click.stop="cancel"
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
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {computed, ref, watch} from 'vue'
import {createTopic} from '@/api/topics'
import {find, trim} from 'lodash'
import {putFocusNextTick} from '@/lib/utils'

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

const isSaving = ref(false)
const maxLabelLength = ref(50)
const minLabelLength = ref(3)
const showEditTopicModal = ref(false)
const topic = ref(undefined)
const disableSaveButton = computed(() => {
  return !isValidLabel.value || isSaving.value || isLabelReserved.value
})
const isLabelReserved = computed(() => {
  return !!find(props.allTopics, t => {
    const trimmed = trim(topic.value)
    return t.topic.toLowerCase() === trimmed.toLowerCase()
  })
})
const isValidLabel = computed(() => {
  return trim(topic.value).length >= minLabelLength.value
})

watch(showEditTopicModal, () => {
  if (showEditTopicModal.value) {
    putFocusNextTick('create-topic-input')
  }
})

const cancel = () => {
  showEditTopicModal.value = false
  props.onCancel()
}

const init = () => {
  topic.value = ''
  showEditTopicModal.value = true
}

const save = () => {
  isSaving.value = true
  topic.value = trim(topic.value)
  createTopic(topic.value).then(data => {
    props.afterSave(data)
    isSaving.value = false
    showEditTopicModal.value = false
  })
}

init()
</script>

<style scoped>
.text-field-width {
  width: 350px;
}
</style>
