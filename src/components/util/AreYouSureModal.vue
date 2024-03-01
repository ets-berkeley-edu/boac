<template>
  <b-modal
    v-model="showAreYouSureModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="functionCancel"
    @hide.prevent="functionCancel"
    @shown="putFocusNextTick('modal-header')"
  >
    <div>
      <ModalHeader clazz="px-3" :text="modalHeader" />
      <div v-if="modalBody" class="modal-body">
        <div class="px-3">
          <span v-html="modalBody" />
        </div>
      </div>
      <div class="modal-footer mb-0 pb-0 pt-3">
        <form @submit.prevent="confirm">
          <v-btn
            id="are-you-sure-confirm"
            class="btn-primary-color-override"
            :disabled="isProcessing"
            @click.prevent="confirm"
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
            class="pl-2"
            :disabled="isProcessing"
            variant="plain"
            @click.stop="functionCancel"
          >
            {{ buttonLabelCancel }}
          </v-btn>
        </form>
      </div>
    </div>
  </b-modal>
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
    modalBody: {
      type: String,
      required: false,
      default: null
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
    }
  }
}
</script>
