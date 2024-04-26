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
      <ModalHeader text="Delete Saved Cohort" />
      <hr />
      <div class="px-4 py-2">
        Are you sure you want to delete "<strong>{{ useCohortStore().cohortName }}</strong>"?
      </div>
      <hr />
      <div aria-live="polite">
        <v-alert
          v-if="error && !isDeleting"
          class="font-size-15 mx-4 mb-2"
          color="error"
          density="compact"
          :icon="mdiAlert"
          :text="error"
          title="Error"
          variant="tonal"
        />
      </div>
      <div class="d-flex justify-end px-4 py-2">
        <ProgressButton
          id="delete-cohort-confirm"
          :action="onConfirm"
          :in-progress="isDeleting"
          size="large"
          text="Delete"
        />
        <v-btn
          id="delete-cohort-cancel"
          class="ml-1"
          text="Cancel"
          variant="plain"
          @click="cancelDeleteModal"
        />
      </div>
    </v-card>
  </v-overlay>
</template>

<script setup>
import {mdiAlert} from '@mdi/js'
import {useCohortStore} from '@/stores/cohort-edit-session'
</script>

<script>
import ModalHeader from '@/components/util/ModalHeader'
import ProgressButton from '@/components/util/ProgressButton'
import {putFocusNextTick} from '@/lib/utils'

export default {
  name: 'DeleteCohortModal',
  components: {ModalHeader, ProgressButton},
  props: {
    cancelDeleteModal: {
      required: true,
      type: Function
    },
    deleteCohort: {
      required: true,
      type: Function
    },
    error: {
      default: undefined,
      required: false,
      type: String
    },
    showModal: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    isDeleting: false
  }),
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      }
    }
  },
  methods: {
    onConfirm() {
      this.isDeleting = true
      this.deleteCohort().then(() => this.isDeleting = false)
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
