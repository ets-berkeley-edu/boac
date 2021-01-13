<template>
  <div>
    <ModalHeader text="Remove Drop-in Scheduler" />
    <div id="confirm-remove-scheduler-body" class="modal-body">
      Are you sure you want to remove
      <strong :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ schedulerName }}</strong>
      as a drop-in scheduler?
    </div>
    <div class="modal-footer">
      <form @submit.prevent="removeScheduler">
        <b-btn
          id="remove-scheduler-confirm"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="removeScheduler"
        >
          Remove
        </b-btn>
        <b-btn
          id="remove-scheduler-cancel"
          class="pl-2"
          variant="link"
          @click="cancelModal"
        >
          Cancel
        </b-btn>
      </form>
    </div>
  </div>
</template>

<script>
import ModalHeader from '@/components/util/ModalHeader'

export default {
  name: 'RemoveDropInSchedulerModal',
  components: {ModalHeader},
  props: {
    cancelModal: Function,
    removeScheduler: Function,
    schedulerName: String,
    schedulerUid: String
  }
}
</script>
