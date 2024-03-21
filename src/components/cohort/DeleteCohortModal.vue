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
        Are you sure you want to delete "<strong>{{ cohortName }}</strong>"?
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
        ></v-alert>
      </div>
      <div class="d-flex justify-end px-4 py-2">
        <ProgressButton
          id="delete-cohort-confirm"
          :action="onConfirm"
          :in-progress="isDeleting"
        >
          Delete
        </ProgressButton>
        <v-btn
          id="delete-cohort-cancel"
          class="ml-1"
          variant="plain"
          @click="cancelDeleteModal"
        >
          Cancel
        </v-btn>
      </div>
    </v-card>
  </v-overlay>
</template>

<script setup>
import {mdiAlert} from '@mdi/js'
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
    cohortName: {
      required: true,
      type: String
    },
    deleteCohort: {
      required: true,
      type: Function
    },
    error: {
      default: undefined,
      type: String,
      required: false
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    isDeleting: false
  }),
  computed: {
    showModalProxy: {
      get() {
        return this.showModal
      },
      set(value) {
        this.toggleShow(value)
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
