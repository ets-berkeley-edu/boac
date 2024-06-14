<template>
  <v-dialog
    v-model="model"
    persistent
    retain-focus
    width="auto"
    @update:model-value="onToggle"
  >
    <v-card min-width="600">
      <v-card-title>
        <ModalHeader class="ml-2 mt-2" :text="modalHeader" />
      </v-card-title>
      <v-card-text class="py-2">
        {{ text }}
        <slot />
      </v-card-text>
      <v-card-actions class="float-right pb-5 pr-6">
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
    </v-card>
  </v-dialog>
</template>

<script setup>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'
import {ref} from 'vue'

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
  text: {
    type: String,
    required: false,
    default: ''
  }
})
let isProcessing = ref(false)

// eslint-disable-next-line vue/require-prop-types
const model = defineModel()

const confirm = () => {
  isProcessing.value = true
  const result = props.functionConfirm()
  if (result && typeof result.then === 'function') {
    result.then(() => isProcessing.value = false)
  } else {
    isProcessing.value = false
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
