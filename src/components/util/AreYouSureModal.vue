<template>
  <v-dialog
    v-model="showAreYouSureModal"
    persistent
    @update:model-value="onToggle"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <div class="mx-10 my-4">
        <ModalHeader :text="modalHeader" />
        <div class="mb-6 mt-2">
          <slot />
        </div>
        <div class="float-right">
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
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {watch} from 'vue'

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
  },
  showModal: {
    type: Boolean,
    required: true
  }
})
let isProcessing = false
let showAreYouSureModal = props.showModal

watch(() => props.showModal, value => showAreYouSureModal = value)

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
