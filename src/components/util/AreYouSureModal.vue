<template>
  <v-overlay
    v-model="showAreYouSureModal"
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
      <ModalHeader clazz="px-3" :text="modalHeader" />
      <div class="px-4 mt-4">
        <slot></slot>
      </div>
      <hr />
      <form @submit.prevent="confirm">
        <div class="d-flex justify-end py-3 px-4">
          <ProgressButton
            id="are-you-sure-confirm"
            :action="confirm"
            :disabled="isProcessing"
            :in-progress="isProcessing"
          >
            {{ buttonLabelConfirm }}
          </ProgressButton>
          <v-btn
            id="are-you-sure-cancel"
            :disabled="isProcessing"
            variant="plain"
            @click.stop="functionCancel"
          >
            {{ buttonLabelCancel }}
          </v-btn>
        </div>
      </form>
    </v-card>
  </v-overlay>
</template>

<script>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import Util from '@/mixins/Util'

export default {
  name: 'AreYouSureModal',
  components: {ModalHeader, ProgressButton},
  mixins: [Util],
  props: {
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
  },
  data: () => ({
    isProcessing: false,
    showAreYouSureModal: false
  }),
  watch: {
    showModal(value) {
      this.showAreYouSureModal = value
    }
  },
  created() {
    this.showAreYouSureModal = this.showModal
  },
  methods: {
    confirm() {
      this.isProcessing = true
      const result = this.functionConfirm()
      if (result && typeof result.then === 'function') {
        result.then(() => {
          this.isProcessing = false
        })
      } else {
        this.isProcessing = false
      }
    },
    onToggle(isOpen) {
      if (isOpen) {
        this.putFocusNextTick('modal-header')
      } else {
        this.functionCancel()
      }
    }
  }
}
</script>
