<template>
  <div>
    <div class="modal-header">
      <h3 id="confirm-remove-scheduler-header">Remove Drop-in Scheduler</h3>
    </div>
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
          @click.prevent="removeScheduler">
          Remove
        </b-btn>
        <b-btn
          id="remove-scheduler-cancel"
          class="pl-2"
          variant="link"
          @click="cancelModal">
          Cancel
        </b-btn>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RemoveDropInSchedulerModal',
  props: {
    cancelModal: Function,
    removeScheduler: Function,
    schedulerName: String,
    schedulerUid: String
  }
};
</script>
