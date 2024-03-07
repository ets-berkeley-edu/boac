<template>
  <v-overlay
    v-model="showAreYouSureModal"
    class="justify-center overflow-auto"
    max-width="800"
    min-width="400"
    persistent
    width="100%"
    @update:model-value="onToggle"
  >
    <v-card class="modal-content">
      <ModalHeader clazz="px-3" :text="modalHeader" />
      <hr />
      <div class="px-4">
        <slot></slot>
      </div>
      <hr />
      <form @submit.prevent="confirm">
        <div class="d-flex justify-end py-3 px-4">
          <v-btn
            id="are-you-sure-confirm"
            color="primary"
            :disabled="isProcessing"
            @click.prevent.once="confirm"
          >
            <v-progress-circular
              v-if="isProcessing"
              class="mr-1"
              size="small"
            />
            {{ buttonLabelConfirm }}
          </v-btn>
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
import Util from '@/mixins/Util'

export default {
  name: 'AreYouSureModal',
  components: {ModalHeader},
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
