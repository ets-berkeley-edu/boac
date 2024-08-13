<template>
  <v-dialog
    v-model="showModalProxy"
    class="justify-center overflow-auto"
    persistent
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card
      class="modal-content"
      min-width="400"
      max-width="600"
    >
      <v-card-title>
        <ModalHeader class="ml-2" text="FERPA Reminder" />
      </v-card-title>
      <v-card-text class="py-2">
        <FerpaReminder />
      </v-card-text>
      <v-card-actions class="float-right pb-3 pr-6">
        <ProgressButton
          id="are-you-sure-confirm"
          :action="confirm"
          :disabled="isDownloading"
          :in-progress="isDownloading"
          text="I understand"
        />
        <v-btn
          id="ferpa-reminder-cancel"
          class="ml-1"
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
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'
import {putFocusNextTick} from '@/lib/utils'
import {computed} from 'vue'
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

const onToggle = isOpen => {
  if (isOpen) {
    putFocusNextTick('modal-header')
  } else {
    props.cancel()
  }
}
</script>
