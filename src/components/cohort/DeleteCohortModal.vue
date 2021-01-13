<template>
  <div>
    <ModalHeader text="Delete Saved Cohort" />
    <div class="modal-body cohort-label">
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
import ModalHeader from '@/components/util/ModalHeader'

export default {
  name: 'DeleteCohortModal',
  components: {ModalHeader},
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
