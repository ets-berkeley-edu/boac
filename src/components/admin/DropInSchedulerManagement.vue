<template>
  <div id="drop-in-scheduler-management" class="pt-4 pr-4">
    <h2 class="page-section-header-sub">Drop-in Scheduler Management ({{ dept.name }})</h2>
    <div class="mb-2">
      <span id="add-scheduler-input-label" class="sr-only">Choose a scheduler. Expect auto-suggest as you type name or SID.</span>
      <Autocomplete
        id="add-scheduler-input"
        class="w-50"
        :add-selection="addScheduler"
        :demo-mode-blur="true"
        input-labelled-by="add-scheduler-input-label"
        placeholder="Add scheduler by name or SID"
        :show-add-button="true"
        :source="schedulersByNameOrSid"
      />
    </div>
    <b-container v-if="schedulers.length" id="scheduler-rows" class="m-3 w-50">
      <b-row
        v-for="scheduler in schedulers"
        :id="`scheduler-row-${scheduler.uid}`"
        :key="scheduler.uid"
        align-v="start"
        class="p-2"
      >
        <b-col
          :id="`scheduler-row-${scheduler.uid}-name`"
          class="font-weight-500 no-wrap"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        >
          {{ scheduler.lastName }}, {{ scheduler.firstName }}
        </b-col>
        <b-col
          :id="`scheduler-row-${scheduler.uid}-sid`"
          :class="{'demo-mode-blur': $currentUser.inDemoMode}"
        >
          {{ scheduler.csid }}
        </b-col>
        <b-col class="d-flex justify-content-end">
          <b-btn
            v-if="!isRemoving || scheduler.uid !== schedulerToRemove.uid"
            :id="`scheduler-row-${scheduler.uid}-remove-button`"
            class="btn btn-link p-0"
            variant="link"
            @click="confirmRemoveScheduler(scheduler)"
            @keyup.enter="confirmRemoveScheduler(scheduler)"
          >
            Remove
          </b-btn>
          <div v-if="isRemoving && scheduler.uid === schedulerToRemove.uid">
            <font-awesome icon="spinner" spin />
          </div>
        </b-col>
      </b-row>
    </b-container>
    <b-modal
      v-model="showRemoveSchedulerModal"
      body-class="pl-0 pr-0"
      hide-footer
      hide-header
      @shown="$putFocusNextTick('modal-header')"
    >
      <RemoveDropInSchedulerModal
        :cancel-modal="cancelRemoveSchedulerModal"
        :remove-scheduler="removeScheduler"
        :scheduler-name="`${$_.get(schedulerToRemove, 'firstName')} ${$_.get(schedulerToRemove, 'lastName')}`"
      />
    </b-modal>
  </div>
</template>

<script>
import Autocomplete from '@/components/util/Autocomplete'
import Context from '@/mixins/Context'
import RemoveDropInSchedulerModal from '@/components/admin/RemoveDropInSchedulerModal'
import Util from '@/mixins/Util'
import {findStudentsByNameOrSid} from '@/api/student'
import {addDropInScheduler, removeDropInScheduler} from '@/api/user'

export default {
  name: 'DropInSchedulerManagement',
  components: {
    Autocomplete,
    RemoveDropInSchedulerModal
  },
  mixins: [Context, Util],
  props: {
    dept: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    isRemoving: false,
    schedulers: [],
    schedulerToRemove: null,
    showRemoveSchedulerModal: false
  }),
  created() {
    this.schedulers = this.dept.schedulers
  },
  methods: {
    addScheduler(scheduler) {
      return addDropInScheduler(this.dept.code, scheduler.uid).then(updatedDept => {
        this.schedulers = updatedDept.schedulers
      })
    },
    cancelRemoveSchedulerModal() {
      this.showRemoveSchedulerModal = false
      this.alertScreenReader(`Cancel removal of ${this.schedulerToRemove.firstName} ${this.schedulerToRemove.lastName}`)
    },
    confirmRemoveScheduler(scheduler) {
      this.showRemoveSchedulerModal = true
      this.schedulerToRemove = scheduler
    },
    removeScheduler() {
      this.alertScreenReader(`Removing ${this.schedulerToRemove.firstName} ${this.schedulerToRemove.lastName}`)
      this.showRemoveSchedulerModal = false
      this.isRemoving = true
      removeDropInScheduler(this.dept.code, this.schedulerToRemove.uid).then(updatedDept => {
        this.schedulers = updatedDept.schedulers
        this.isRemoving = false
      })
    },
    schedulersByNameOrSid(query, limit) {
      const csids = this.$_.map(this.dept.schedulers, 'csid')
      return new Promise(resolve => {
        findStudentsByNameOrSid(query, limit).then(students => {
          resolve(this.$_.filter(students, s => !this.$_.includes(csids, s.sid)))
        })
      })
    }
  }
}
</script>
