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
      <ModalHeader :text="modalHeader" />
      <div v-if="modalBody" class="modal-body">
        <span v-html="modalBody"></span>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="functionConfirm">
          <b-btn
            id="are-you-sure-confirm"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="functionConfirm"
          >
            {{ buttonLabelConfirm }}
          </b-btn>
          <b-btn
            id="are-you-sure-cancel"
            class="pl-2"
            variant="link"
            @click.stop="functionCancel"
          >
            {{ buttonLabelCancel }}
          </b-btn>
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
    showAreYouSureModal: false
  }),
  watch: {
    showModal(value) {
      this.showAreYouSureModal = value
    }
  },
  created() {
    this.showAreYouSureModal = this.showModal
  }
}
</script>
