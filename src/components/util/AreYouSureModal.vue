<template>
  <v-dialog
    v-model="model"
    persistent
    width="auto"
    @update:model-value="onToggle"
  >
    <v-card class="modal-content" min-width="600">
      <div>
        <v-card-title class="px-8">
          <ModalHeader :text="modalHeader" />
        </v-card-title>
        <v-card-text class="px-8 pb-3">
          <slot />
        </v-card-text>
        <v-card-actions class="float-right pr-6">
          <ProgressButton
            id="are-you-sure-confirm"
            :action="confirm"
            :disabled="isProcessing"
            :in-progress="isProcessing"
            :text="buttonLabelConfirm"
          />
          <v-btn
            id="are-you-sure-cancel"
            class="ml-1"
            :disabled="isProcessing"
            :text="buttonLabelCancel"
            variant="plain"
            @click="functionCancel"
          />
        </v-card-actions>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'

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
    type: Function,
    required: true
  },
  functionConfirm: {
    type: Function,
    required: true
  },
  modalHeader: {
    type: String,
    required: false,
    default: 'Are you sure?'
  }
})
let isProcessing = false

// eslint-disable-next-line vue/require-prop-types
const model = defineModel()

const confirm = () => {
  isProcessing = true
  const result = props.functionConfirm()
  if (result && typeof result.then === 'function') {
    result.then(() => isProcessing = false)
  } else {
    isProcessing = false
  }
}

const onToggle = isOpen => {
  if (isOpen) {
    putFocusNextTick('modal-header')
  } else {
    props.functionCancel()
  }
}
</script>
