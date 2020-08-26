<template>
  <b-modal
    v-if="!isNil(dropInAdvisors)"
    id="advising-appointment-assign"
    v-model="showAppointmentAssignModal"
    :no-close-on-backdrop="true"
    body-class="pl-0 pr-0"
    hide-footer
    hide-header
    @cancel.prevent="close"
    @hide.prevent="close">
    <div>
      <div class="modal-header">
        <h3 :class="{'demo-mode-blur': $currentUser.inDemoMode}">{{ appointment.student.name }}</h3>
      </div>
      <div class="modal-body w-100">
        <div v-if="dropInAdvisors.length" class="pb-3 pt-3">
          <label for="assign-modal-advisor-select" class="font-weight-bolder">
            Select a drop-in advisor:
          </label>
          <b-form-select
            id="assign-modal-advisor-select"
            v-model="selectedAdvisorUid">
            <template v-slot:first>
              <option :value="null">Select...</option>
            </template>
            <option
              v-for="advisor in dropInAdvisors"
              :key="advisor.uid"
              :value="advisor.uid">
              {{ advisor.name }}
            </option>
          </b-form-select>
        </div>
        <div v-if="!dropInAdvisors.length" class="has-error pb-1 pt-1">
          Sorry, no advisors are on duty.
        </div>
      </div>
      <div class="modal-footer">
        <form @submit.prevent="assign">
          <b-btn
            v-if="dropInAdvisors.length"
            id="btn-appointment-assign"
            aria-label="Assign appointment"
            :disabled="!selectedAdvisorUid"
            class="btn-primary-color-override"
            variant="primary"
            @click.prevent="assign">
            Assign
          </b-btn>
          <b-btn
            id="btn-appointment-close"
            class="pl-2"
            variant="link"
            @click.stop="close">
            Close
          </b-btn>
        </form>
      </div>
    </div>
  </b-modal>
</template>

<script>
import Berkeley from '@/mixins/Berkeley'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { getDropInAdvisorsForDept } from '@/api/user'

export default {
  name: 'AppointmentAssignModal',
  mixins: [Berkeley, Context, Util],
  props: {
    appointment: {
      type: Object,
      required: true
    },
    appointmentAssign: {
      type: Function,
      required: true
    },
    close: {
      type: Function,
      required: true
    },
    showModal: {
      type: Boolean,
      required: true
    }
  },
  data: () => ({
    dropInAdvisors: undefined,
    selectedAdvisorUid: null,
    showAppointmentAssignModal: false
  }),
  watch: {
    showModal(value) {
      this.showAppointmentAssignModal = value
    }
  },
  created() {
    this.showAppointmentAssignModal = this.showModal
    getDropInAdvisorsForDept(this.appointment.deptCode).then(dropInAdvisors => {
      this.dropInAdvisors = this.$_.filter(dropInAdvisors, a => {
        return a.available || a.uid === this.$currentUser.uid
      })
    })
  },
  methods: {
    assign() {
      const advisor = this.find(this.dropInAdvisors, {'uid': this.selectedAdvisorUid})
      if (advisor) {
        this.appointmentAssign(advisor)
      }
      this.alertScreenReader(`Assigned to ${advisor.name}`)
      this.showAppointmentAssignModal = false
    }
  }
}
</script>
