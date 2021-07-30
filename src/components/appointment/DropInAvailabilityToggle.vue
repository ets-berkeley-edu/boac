<template>
  <div>
    <div v-if="!$_.isNil(isAvailable)" class="availability-status-outer flex-row">
      <div v-if="isHomepage" class="mr-2 availability-status">
        My availability:
      </div>
      <div
        v-if="!isAvailable || !$currentUser.isAdmin"
        :class="isAvailable ? 'availability-status-disabled' : 'availability-status-active'"
        class="aria-hidden availability-status"
      >
        Off duty
      </div>
      <div v-if="!$currentUser.isAdmin" class="toggle-btn-column">
        <button
          v-if="!isToggling"
          :id="buttonElementId"
          type="button"
          class="btn btn-link pt-0 pb-0 pl-1 pr-1"
          @click="toggle"
          @keyup.down="toggle"
        >
          <span class="status-toggle-label">
            <font-awesome v-if="isAvailable" icon="toggle-on" class="toggle toggle-on"></font-awesome>
            <font-awesome v-if="!isAvailable" icon="toggle-off" class="toggle toggle-off"></font-awesome>
            <span class="sr-only">{{ isAvailable ? 'On duty' : 'Off duty' }}</span>
          </span>
        </button>
        <div v-if="isToggling" class="pl-2">
          <font-awesome icon="spinner" spin />
        </div>
      </div>
      <div
        v-if="isAvailable || !$currentUser.isAdmin"
        :class="isAvailable ? 'availability-status-active' : 'availability-status-disabled'"
        class="aria-hidden availability-status"
      >
        On duty
      </div>
    </div>
    <AreYouSureModal
      v-if="showOffDutyConfirmModal"
      :function-cancel="cancelGoOffDuty"
      :function-confirm="confirmGoOffDuty"
      :modal-body="offDutyConfirmModalBody()"
      :show-modal="showOffDutyConfirmModal"
      button-label-confirm="Confirm"
      modal-header="Go off duty?"
    />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import {setDropInAvailability} from '@/api/user'

export default {
  name: 'DropInAvailabilityToggle',
  components: {
    AreYouSureModal
  },
  mixins: [Context, Util],
  props: {
    availability: {
      type: Boolean,
      required: true
    },
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
    uid: {
      type: String,
      required: true
    }
  },
  data: () => ({
    isAvailable: undefined,
    isToggling: undefined,
    showOffDutyConfirmModal: false
  }),
  computed: {
    buttonElementId() {
      return `toggle-drop-in-availability-${this.uid === this.$currentUser.uid ? 'me' : this.uid}`
    }
  },
  watch: {
    availability(value) {
      this.isAvailable = value
    }
  },
  created() {
    this.isAvailable = this.availability
  },
  methods: {
    cancelGoOffDuty() {
      this.showOffDutyConfirmModal = false
      this.$nextTick(() => {
        this.selectedStatus = this.status
      })
    },
    confirmGoOffDuty() {
      this.showOffDutyConfirmModal = false
      return this.confirmChangeAvailability(false)
    },
    confirmChangeAvailability(newStatus) {
      this.isToggling = true
      return setDropInAvailability(this.deptCode, this.uid, newStatus).then(() => {
        this.isAvailable = newStatus
        this.isToggling = false
        this.alertScreenReader(`Switching drop-in availability ${this.isAvailable ? 'off' : 'on' }`)
        this.$putFocusNextTick(this.buttonElementId)
      })
    },
    offDutyConfirmModalBody() {
      return `
        Setting status to "Off Duty" will unassign
        ${this.pluralize('assigned student', this.reservedAppointments.length)}
        on the waitlist.`
    },
    toggle: function() {
      const newStatus = !this.isAvailable
      if (!newStatus && this.reservedAppointments.length) {
        this.showOffDutyConfirmModal = true
      } else {
        this.confirmChangeAvailability(newStatus)
      }
    }
  }
}
</script>

<style scoped>
.availability-status {
  font-size: 12px;
  text-transform: uppercase;
}
.availability-status-active {
  font-weight: 600;
}
.availability-status-disabled {
  color: #999999;
}
.availability-status-outer {
  align-items: center;
}
.toggle {
 font-size: 20px;
}
.toggle-btn-column {
  min-height: 28px;
  min-width: 36px;
}
.toggle-off {
   color: #999999;
}
.toggle-on {
   color: #00c13a;
}
</style>
