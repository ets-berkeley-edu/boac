<template>
  <v-dialog
    v-model="showModalProxy"
    aria-describedby="ferpa-reminder-text"
    aria-labelledby="modal-header"
    @keydown.esc="cancel"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <FocusLock>
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
            variant="text"
            @click="cancel"
          >
            Cancel
          </v-btn>
        </v-card-actions>
      </FocusLock>
    </v-card>
  </v-dialog>
</template>

<script setup>
import {computed, watch} from 'vue'
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'
import {putFocusNextTick} from '@/lib/utils'
import ProgressButton from '@/components/util/ProgressButton.vue'

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
