<template>
  <v-dialog
    v-model="showModalProxy"
    aria-describedby="ferpa-reminder-text"
    aria-labelledby="modal-header"
    persistent
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <FocusLock @keydown.esc="cancel">
        <v-card-title>
          <ModalHeader text="FERPA Reminder" />
        </v-card-title>
        <v-card-text id="ferpa-reminder-text" class="modal-body">
          <FerpaReminder />
        </v-card-text>
        <v-card-actions class="modal-footer">
          <ProgressButton
            id="are-you-sure-confirm"
            :action="confirm"
            :disabled="isDownloading"
            :in-progress="isDownloading"
            text="I understand"
          />
          <v-btn
            id="ferpa-reminder-cancel"
            class="ml-2"
            :disabled="isDownloading"
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
import FerpaReminder from '@/components/util/FerpaReminder'
import FocusLock from 'vue-focus-lock'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {computed, watch} from 'vue'
import {putFocusNextTick} from '@/lib/utils'

const props = defineProps({
  cancel: {
    required: true,
    type: Function
  },
  confirm: {
    required: true,
    type: Function
  },
  isDownloading: {
    type: Boolean,
    required: false
  },
  showModal: {
    type: Boolean,
    required: true
  }
})

const showModalProxy = computed(() => {
  return props.showModal
})

watch(showModalProxy, isOpen => {
  if (isOpen) {
    putFocusNextTick('are-you-sure-confirm')
  } else {
    props.cancel()
  }
})
</script>
