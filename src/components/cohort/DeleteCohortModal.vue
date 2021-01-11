<template>
  <div>
    <div class="modal-header">
      <h3 id="confirm-delete-header">Delete Saved Cohort</h3>
    </div>
    <div id="confirm-delete-body" class="modal-body cohort-label">
      Are you sure you want to delete "<strong>{{ cohortName }}</strong>"?
    </div>
    <div class="modal-footer">
      <form @submit.prevent="deleteCohort">
        <b-btn
          id="delete-confirm"
          class="btn-primary-color-override"
          variant="primary"
          @click.prevent="deleteCohort"
        >
          Delete
        </b-btn>
        <b-btn
          id="delete-cancel"
          class="pl-2"
          variant="link"
          @click="cancelDeleteModal"
        >
          Cancel
        </b-btn>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeleteCohortModal',
  props: {
    cancelDeleteModal: Function,
    cohortName: String,
    deleteCohort: Function
  }
}
</script>

<style scoped>
.cohort-label {
  word-wrap: break-word;
}
</style>
