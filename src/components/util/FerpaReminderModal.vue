<template>
  <v-dialog
    v-model="showModalProxy"
    aria-describedby="ferpa-reminder-text"
    aria-labelledby="modal-header"
    class="justify-center overflow-auto"
    persistent
    width="100%"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <v-card-title>
        <ModalHeader class="ml-2" text="FERPA Reminder" />
      </v-card-title>
      <v-card-text id="ferpa-reminder-text">
        <FerpaReminder />
      </v-card-text>
      <v-card-actions class="d-flex justify-end">
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
          variant="plain"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </v-card-actions>
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
