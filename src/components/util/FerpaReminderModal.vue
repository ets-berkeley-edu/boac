<template>
  <v-overlay
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
      <ModalHeader text="FERPA Reminder" />
      <FerpaReminder />
      <div class="d-flex justify-end py-3 px-4">
        <v-btn
          id="ferpa-reminder-confirm"
          @click="onClickConfirm"
        >
          I understand
        </v-btn>
        <v-btn
          id="ferpa-reminder-cancel"
          class="pl-2"
          variant="plain"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </v-card>
  </v-overlay>
</template>

<script>
import FerpaReminder from '@/components/util/FerpaReminder'
import ModalHeader from '@/components/util/ModalHeader'
import {putFocusNextTick} from '@/lib/utils'

export default {
  name: 'ExportListModal',
  components: {FerpaReminder, ModalHeader},
  props: {
    cancel: {
      required: true,
      type: Function
    },
    confirm: {
      required: true,
      type: Function
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      },
      set(value) {
        this.toggleShow(value)
      }
    }
  },
  methods: {
    onClickConfirm() {
      this.confirm()
    },
    onToggle(isOpen) {
      if (isOpen) {
        putFocusNextTick('modal-header')
      } else {
        this.cancel()
      }
    }
  }
}
</script>
