<template>
  <v-dialog
    v-model="model"
    aria-describedby="are-you-sure-text"
    aria-labelledby="are-you-sure-header"
    persistent
  >
    <v-card class="modal-content" min-width="600">
      <FocusLock :disabled="!focusLocked">
        <v-card-title>
          <ModalHeader header-id="are-you-sure-header" :text="modalHeader" />
        </v-card-title>
        <v-card-text id="are-you-sure-text" class="modal-body">
          <span v-html="text" />
          <slot />
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="are-you-sure-confirm"
            :action="confirm"
            :disabled="isProcessing"
            :in-progress="isProcessing"
            :text="buttonLabelConfirm"
          />
          <v-btn
            v-if="functionCancel"
            id="are-you-sure-cancel"
            class="ml-2"
            :disabled="isProcessing"
            :text="buttonLabelCancel"
            variant="text"
            @click="functionCancel"
          />
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {ref, watch} from 'vue'

const props = defineProps({
  buttonLabelCancel: {
    type: String,
    required: false,
    default: 'Cancel'
  },
  buttonLabelConfirm: {
    type: String,
    required: false,
    default: 'Confirm'
  },
  functionCancel: {
    default: undefined,
    required: false,
    type: Function
  },
  functionConfirm: {
    type: Function,
    required: true
  },
  modalHeader: {
    type: String,
    required: false,
    default: 'Are you sure?'
  },
  text: {
    type: String,
    required: false,
    default: ''
  }
})
let isProcessing = ref(false)

const focusLocked = ref(false)
// eslint-disable-next-line vue/require-prop-types
const model = defineModel()

watch(model, isOpen => {
  if (isOpen) {
    setTimeout(() => focusLocked.value = isOpen, 500)
    putFocusNextTick('are-you-sure-confirm')
  }
})

const confirm = () => {
  isProcessing.value = true
  const result = props.functionConfirm()
  if (result && typeof result.then === 'function') {
    result.then(() => isProcessing.value = false)
  } else {
    isProcessing.value = false
  }
}
</script>
