<template>
  <div>
    <div class="modal-header">
      <h3 id="confirm-delete-header">Delete Saved Cohort</h3>
    </div>
    <div class="modal-body cohort-label" id="confirm-delete-body">
      Are you sure you want to delete "<strong>{{ cohortName }}</strong>"?
    </div>
    <div class="modal-footer">
      <form @submit.prevent="deleteCohort()">
        <b-btn id="confirm-delete-btn"
               variant="primary"
               v-focus
               @click.prevent="deleteCohort()">Delete</b-btn>
        <b-btn id="cancel-delete-btn"
               class="pl-2"
               variant="link"
               @click="cancelDeleteModal()">Cancel</b-btn>
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
};
</script>

<style scoped>
</style>
