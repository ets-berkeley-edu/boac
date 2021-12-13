<template>
  <div>
    <CreateAppointmentModal
      v-if="showCreateAppointmentModal"
      :advisors="advisors"
      :cancel="cancelCreateAppointment"
      :create-appointment="createAppointment"
      :dept-code="deptCode"
      :show-modal="showCreateAppointmentModal"
      :waitlist-unresolved="waitlist.unresolved"
    />
    <LogResolvedIssueModal
      v-if="showLogResolvedIssueModal"
      :cancel="cancelLogResolvedIssue"
      :log-resolved-issue="logResolvedIssue"
      :show-modal="showLogResolvedIssueModal"
      :waitlist-unresolved="waitlist.unresolved"
    />
    <div v-if="isHomepage" class="pb-2">
      <div class="align-items-center d-flex homepage-header-border justify-content-between mb-2">
        <div aria-live="polite" role="alert">
          <h2 class="page-section-header">Drop-in Waitlist - {{ $moment() | moment('MMM D') }}</h2>
        </div>
        <div v-if="!$currentUser.isAdmin">
          <b-btn
            id="btn-homepage-create-appointment"
            variant="link"
            class="mb-1"
            @click="showCreateAppointmentModal = true"
          >
            <font-awesome icon="plus" />
            <span class="sr-only">Create appointment</span>
          </b-btn>
        </div>
      </div>
      <div>
        <DropInAvailabilityToggle
          :availability="dropInAvailability"
          :dept-code="deptCode"
          :is-homepage="isHomepage"
          :reserved-appointments="myReservedAppointments"
          :uid="$currentUser.uid"
        />
      </div>
      <div>
        <b-form @submit.prevent="submitDropInStatus">
          <div
            class="d-flex mt-1 mb-2"
            :class="(dropInStatus && !dropInStatusLoading) ? 'drop-in-status-outer' : 'align-items-center drop-in-status-form'"
          >
            <div class="pr-2">
              <label class="drop-in-status-label" for="drop-in-status-input">My Status:</label>
            </div>
            <div v-if="dropInStatusLoading">
              <font-awesome icon="spinner" spin />
            </div>
            <div :class="{'flex-grow-1 pr-3': !dropInStatus}">
              <b-form-input
                v-if="!dropInStatus && !dropInStatusLoading"
                id="drop-in-status-input"
                v-model="dropInStatusNew"
                class="drop-in-status-input"
                maxlength="255"
              ></b-form-input>
            </div>
            <div v-if="!dropInStatus">
              <b-btn
                v-if="!dropInStatusLoading"
                id="drop-in-status-submit"
                class="btn-primary-color-override"
                :disabled="!dropInStatusNew"
                type="submit"
                variant="primary"
              >
                Save
              </b-btn>
            </div>
            <div v-if="dropInStatus && !dropInStatusLoading">
              <div class="align-items-start d-flex">
                <div class="drop-in-status-text pr-2">
                  {{ dropInStatus }}
                </div>
                <div class="drop-in-status-clear faint-text pb-1">
                  [<button
                    id="drop-in-status-clear"
                    class="btn btn-link m-0 p-0"
                    @click="clearDropInStatus"
                    @keyup.enter="clearDropInStatus"
                  >
                    Clear<span class="sr-only"> Status</span>
                  </button>]
                </div>
              </div>
            </div>
          </div>
        </b-form>
      </div>
    </div>
    <div v-if="!isHomepage">
      <div class="border-bottom d-flex justify-content-between">
        <div>
          <h1 class="font-size-18 font-weight-bold text-nowrap">
            <span aria-live="polite" role="alert">Today's Drop-In Waitlist ({{ waitlist.unresolved.length }}<span class="sr-only"> students</span>)</span>
          </h1>
        </div>
        <div>
          <h2 id="waitlist-today-date" class="font-size-18 font-weight-bold text-nowrap">{{ $moment() | moment('ddd, MMM D') }}</h2>
        </div>
      </div>
    </div>
    <div v-if="!waitlist.unresolved.length && !waitlist.resolved.length && !creating" class="border-bottom">
      <div
        id="waitlist-is-empty"
        class="font-size-16 mb-3 ml-1 mt-3"
        aria-live="polite"
        role="alert"
      >
        No appointments yet
      </div>
    </div>
    <div v-if="waitlist.unresolved.length || waitlist.resolved.length || creating">
      <b-container fluid class="pl-0 pr-0" :class="{'homepage-header-border': isHomepage}">
        <b-row v-if="waitlist.unresolved.length">
          <span class="sr-only">{{ waitlist.unresolved.length }} appointments not yet checked in</span>
        </b-row>
        <DropInWaitlistAppointment
          v-for="(appointment, index) in waitlist.unresolved"
          :key="appointment.id"
          :appointment="appointment"
          :dept-code="deptCode"
          :is-homepage="isHomepage"
          :is-last="!creating && (index + 1 === waitlist.unresolved.length)"
          :on-appointment-status-change="onAppointmentStatusChange"
        />
        <b-row
          v-if="creating"
          id="waitlist-appointment-creation-spinner"
          no-gutters
          class="font-size-16 mt-2 pb-4 pt-1"
        >
          <b-col sm="12" class="text-center">
            <font-awesome icon="spinner" spin />
          </b-col>
        </b-row>
        <b-row
          :class="waitlist.unresolved.length && waitlist.resolved.length ? 'border-thick-grey' : ''"
          no-gutters
          class="border-top"
        >
          <span v-if="waitlist.resolved.length" class="sr-only">{{ waitlist.resolved.length }} appointments checked in or canceled</span>
        </b-row>
        <DropInWaitlistAppointment
          v-for="appointment in waitlist.resolved"
          :key="appointment.id"
          :appointment="appointment"
          :is-homepage="isHomepage"
          :dept-code="deptCode"
          :on-appointment-status-change="onAppointmentStatusChange"
        />
      </b-container>
    </div>
    <div v-if="isHomepage" class="mt-4">
      <b-container id="on-duty-advisor-list" fluid class="pl-0 pr-0">
        <b-row class="border-bottom pb-2 sortable-table-header" no-gutters>
          <b-col class="heading">On-duty advisor(s)</b-col>
          <b-col class="d-flex justify-content-end">Status</b-col>
        </b-row>
        <b-row
          v-for="advisor in availableAdvisors"
          :id="`advisor-uid-${advisor.uid}`"
          :key="advisor.uid"
          no-gutters
          class="border-bottom font-size-16 mt-2"
        >
          <b-col :id="`advisor-uid-${advisor.uid}-name`" class="pb-2">
            {{ advisor.name }}
          </b-col>
          <b-col :id="`advisor-uid-${advisor.uid}-status`" class="d-flex justify-content-end pb-2">
            <span v-if="advisor.status" class="text-muted">
              {{ advisor.status }}
            </span>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CreateAppointmentModal from '@/components/appointment/CreateAppointmentModal'
import DropInAvailabilityToggle from '@/components/appointment/DropInAvailabilityToggle'
import DropInWaitlistAppointment from '@/components/appointment/DropInWaitlistAppointment'
import LogResolvedIssueModal from '@/components/appointment/LogResolvedIssueModal'
import Util from '@/mixins/Util'
import {create as apiCreate} from '@/api/appointments'
import {setDropInStatus} from '@/api/user'

export default {
  name: 'DropInWaitlist',
  components: {
    CreateAppointmentModal,
    DropInAvailabilityToggle,
    DropInWaitlistAppointment,
    LogResolvedIssueModal
  },
  mixins: [Context, Util],
  props: {
    advisors: {
      type: Array,
      required: true
    },
    deptCode: {
      type: String,
      required: true
    },
    isHomepage: {
      type: Boolean
    },
    onAppointmentStatusChange: {
      type: Function,
      required: true
    },
    waitlist: {
      type: Object,
      required: true
    }
  },
  data: () => ({
    creating: false,
    dropInAvailability: false,
    dropInStatus: null,
    dropInStatusLoading: false,
    dropInStatusNew: undefined,
    linkToStudentProfiles: undefined,
    now: undefined,
    showCreateAppointmentModal: false,
    showLogResolvedIssueModal: false
  }),
  computed: {
    availableAdvisors: function() {
      return this.$_.filter(this.advisors, 'available')
    },
    myReservedAppointments: function() {
      return this.$_.filter(this.waitlist.unresolved, (appt) => {
        return appt.status === 'reserved' && appt.advisorUid === this.$currentUser.uid
      })
    }
  },
  created() {
    const currentUserDropInStatus = this.$_.get(this.$currentUser, 'dropInAdvisorStatus')
    this.linkToStudentProfiles = this.$currentUser.isAdmin || !this.$_.isEmpty(this.currentUserDropInStatus)
    this.now = this.$moment()
    if (this.isHomepage) {
      this.$eventHub.on('drop-in-status-change', newAttributes => {
        this.updateDropInAttributes(newAttributes)
      })
      this.updateDropInAttributes(this.$_.find(currentUserDropInStatus, {'deptCode': this.deptCode.toUpperCase()}))
    }
  },
  methods: {
    cancelCreateAppointment() {
      this.showCreateAppointmentModal = false
      this.$announcer.polite('Dialog closed')
    },
    cancelLogResolvedIssue() {
      this.showLogResolvedIssueModal = false
      this.$announcer.polite('Dialog closed')
    },
    clearDropInStatus() {
      this.dropInStatusLoading = true
      setDropInStatus(this.deptCode).then(response => {
        this.updateDropInAttributes(response)
        this.dropInStatusLoading = false
        this.dropInStatusNew = null
        this.$announcer.polite('Drop-in status cleared')
      })
    },
    createAppointment(
      details,
      student,
      topics,
      advisorUid
    ) {
      this.creating = true
      apiCreate(
        this.deptCode,
        details,
        student.sid,
        'Drop-in',
        topics,
        advisorUid
      ).then(() => {
        this.showCreateAppointmentModal = false
        this.onAppointmentStatusChange().then(() => {
          this.creating = false
          this.$announcer.polite(`${student.label} appointment created`)
          this.$putFocusNextTick(`waitlist-student-${student.sid}`)
        })
      })
    },
    logResolvedIssue(
      details,
      student,
      topics,
      schedulerUid
    ) {
      apiCreate(
        this.deptCode,
        details,
        student.sid,
        'Drop-in',
        topics,
        schedulerUid
      ).then(() => {
        this.showLogResolvedIssueModal = false
        this.onAppointmentStatusChange().then(() => {
          this.$announcer.polite(`Resolved issue for ${student.label}`)
        })
      })
    },
    openCreateAppointmentModal() {
      this.showCreateAppointmentModal = true
      this.$announcer.polite('Create appointment form is open')
    },
    openLogResolvedIssueModal() {
      this.showLogResolvedIssueModal = true
      this.$announcer.polite('Log resolved issue form is open')
    },
    submitDropInStatus() {
      this.dropInStatusLoading = true
      setDropInStatus(this.deptCode, this.dropInStatusNew).then(response => {
        this.updateDropInAttributes(response)
        this.dropInStatusLoading = false
        this.$announcer.polite('Drop-in status updated')
      })
    },
    updateDropInAttributes(attrs) {
      if (attrs) {
        this.dropInAvailability = attrs.available
        this.dropInStatus = attrs.status
      }
    }
  }
}
</script>

<style>
.border-thick-grey {
  border-color: lightgrey !important;
  border-width: 3px !important;
}
.drop-in-status-clear {
  white-space: nowrap;
}
.drop-in-status-form {
  max-height: 48px;
  min-height: 48px;
}
.drop-in-status-outer {
  align-items: top;
  padding-top: 5px;
}
.drop-in-status-text {
  padding-top: 1px;
}
.drop-in-status-label {
  font-size: 12px;
  text-transform: uppercase;
  white-space: nowrap;
}
</style>
