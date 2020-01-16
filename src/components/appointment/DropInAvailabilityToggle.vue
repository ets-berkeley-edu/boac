<template>
  <div>
    <div v-if="!$currentUser.isAdmin" class="availability-status-outer flex-row">
      <b-form-group class="mt-3 mb-3">
        <b-form-radio-group
          :id="toggleElementId"
          v-model="selectedStatus"
          class="drop-in-status-toggle"
          :options="dropInStatusOptions"
          buttons
          button-variant="outline-primary"
          name="drop-in-status-toggle"
          size="sm"
          @change="changeStatus"
        ></b-form-radio-group>
      </b-form-group>
    </div>
    <AreYouSureModal
      v-if="showOffDutyConfirmModal"
      :function-cancel="cancelGoOffDuty"
      :function-confirm="confirmGoOffDuty"
      :modal-body="offDutyConfirmModalBody()"
      :show-modal="showOffDutyConfirmModal"
      button-label-confirm="Confirm"
      modal-header="Go off duty?" />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import Util from '@/mixins/Util';
import { setDropInStatus } from '@/api/user';

export default {
  name: 'DropInAvailabilityToggle',
  components: {
    AreYouSureModal
  },
  mixins: [Context, Util],
  props: {
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean,
      required: true
    },
    reservedAppointments: {
      type: Array,
      required: true
    },
    status: {
      type: String,
      required: true
    },
    uid: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      dropInStatusOptions: [
        { text: 'Off Duty', value: 'off_duty_waitlist'},
        { text: 'Advisor', value: 'on_duty_advisor' },
        { text: 'Supervisor', value: 'on_duty_supervisor' }
      ],
      isToggling: undefined,
      selectedStatus: this.status,
      showOffDutyConfirmModal: false
    }
  },
  computed: {
    toggleElementId() {
      return `toggle-drop-in-status-${this.uid === this.$currentUser.uid ? 'me' : this.uid}`;
    }
  },
  watch: {
    status(value) {
      this.selectedStatus = value;
    }
  },
  created() {
    this.$eventHub.$on('drop-in-status-change', status => {
      this.selectedStatus = status;
    });
  },
  methods: {
    cancelGoOffDuty() {
      this.showOffDutyConfirmModal = false;
      this.$nextTick(() => {
        this.selectedStatus = this.status;
      });
    },
    changeStatus: function(selected) {
      if (selected.startsWith('off_duty') && this.reservedAppointments.length) {
        this.showOffDutyConfirmModal = true;
      } else {
        this.confirmChangeStatus(selected);
      }
    },
    confirmGoOffDuty() {
      this.showOffDutyConfirmModal = false;
      this.confirmChangeStatus('off_duty_waitlist');
    },
    confirmChangeStatus(selected) {
      setDropInStatus(this.deptCode, this.uid, selected).then(() => {
        this.alertScreenReader(`Switching drop-in availability to ${selected}`);
      });
    },
    offDutyConfirmModalBody() {
      return `
        Setting status to "Off Duty" will unassign
        ${this.$options.filters.pluralize('assigned student', this.reservedAppointments.length)}
        on the waitlist.`;
    },
  }
};
</script>

<style scoped>
.availability-status-outer {
  align-items: center;
}
</style>

<style>
.drop-in-status-toggle .btn {
  border-color: #3b7ea5 !important;
  color: #3b7ea5 !important;
}
.drop-in-status-toggle .btn.active {
  background-color: #3b7ea5 !important;
  color: #ffffff !important;
}
.drop-in-status-toggle .btn:hover {
  background-color: #69a6c9 !important;
  color: #ffffff !important;
}
</style>
