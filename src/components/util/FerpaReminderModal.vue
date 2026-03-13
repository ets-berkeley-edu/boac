<template>
  <v-dialog
    v-model="showModalProxy"
    aria-describedby="ferpa-reminder-text"
    aria-labelledby="modal-header"
    class="modal-height-unset"
    :fullscreen="$vuetify.display.xs"
    persistent
  >
    <v-card
      class="modal-content"
      max-width="900"
      width="90vw"
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
            aria-label="Cancel Export"
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
import FocusLock from 'vue-focus-lock'
import {computed, watch} from 'vue'
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick, toggleModalBackgroundDisabled} from '@/lib/utils'

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
  toggleModalBackgroundDisabled(isOpen)
  if (isOpen) {
    putFocusNextTick('are-you-sure-confirm')
  } else {
    props.cancel()
  }
})
</script>
