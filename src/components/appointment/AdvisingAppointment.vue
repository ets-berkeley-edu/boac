<template>
  <div :id="`appointment-${appointment.id}-outer`" class="advising-appointment-outer">
    <div
      v-if="!isOpen"
      :id="`appointment-${appointment.id}-is-closed`"
      :class="{'truncate-with-ellipsis': !isOpen}">
      <span :id="`appointment-${appointment.id}-details-closed`" v-html="appointment.details"></span>
    </div>
    <div v-if="isOpen" :id="`appointment-${appointment.id}-is-open`">
      <div class="mt-2">
        <span :id="`appointment-${appointment.id}-details`" v-html="appointment.details"></span>
      </div>
      <div v-if="!(appointment.status === 'checked_in' && appointment.advisor.title === 'Intake Desk') && !appointment.legacySource" class="mt-3">
        <font-awesome icon="clock" class="status-arrived-icon" />
        <span class="text-secondary ml-1">
          Arrived @
          <span :id="`appointment-${appointment.id}-created-at`">
            {{ datePerTimezone(appointment.createdAt) | moment('h:mma') }}
          </span>
        </span>
      </div>
      <div class="d-flex align-items-center mt-1 mb-3">
        <div v-if="isUserDropInAdvisor(appointment.deptCode) && $_.includes(['waiting', 'reserved'], appointment.status)">
          <DropInAppointmentDropdown
            :appointment="appointment"
            :dept-code="appointment.deptCode"
            :include-details-option="false"
            :on-appointment-status-change="onAppointmentStatusChange"
            :self-check-in="true"
            class="mr-3" />
        </div>
        <div v-if="appointment.status === 'reserved' && ($currentUser.isAdmin || isUserDropInAdvisor(appointment.deptCode))">
          <span class="text-secondary">
            Assigned
            <span v-if="appointment.advisor.id" :id="`appointment-${appointment.id}-assigned-to`">
              to {{ appointment.advisor.id === $currentUser.id ? 'you' : appointment.advisor.name }}
            </span>
          </span>
        </div>
        <div v-if="appointment.status === 'checked_in'">
          <font-awesome icon="calendar-check" class="status-checked-in-icon" />
          <span class="text-secondary ml-1">
            Check In
            <span v-if="appointment.statusDate">
              @ <span :id="`appointment-${appointment.id}-checked-in-at`">{{ datePerTimezone(appointment.statusDate) | moment('h:mma') }}</span>
            </span>
          </span>
        </div>
        <div v-if="appointment.status === 'cancelled'">
          <div>
            <font-awesome icon="calendar-minus" class="status-cancelled-icon" />
            <span class="text-secondary ml-1">
              <span :id="`appointment-${appointment.id}-cancel-reason`">{{ appointment.cancelReason || 'Cancelled' }}</span>
            </span>
          </div>
          <div v-if="appointment.cancelReasonExplained" class="mt-1">
            <span :id="`appointment-${appointment.id}-cancel-explained`">{{ appointment.cancelReasonExplained }}</span>
          </div>
        </div>
      </div>
      <div v-if="appointment.advisor.name && (appointment.status === 'checked_in' || appointment.legacySource)" class="mt-2">
        <a
          v-if="appointment.advisor.uid"
          :id="`appointment-${appointment.id}-advisor-name`"
          :aria-label="`Open UC Berkeley Directory page of ${appointment.advisor.name} in a new window`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${appointment.advisor.name}`"
          target="_blank">{{ appointment.advisor.name }}</a>
        <span v-if="!appointment.advisor.uid" :id="`appointment-${appointment.id}-advisor-name`">
          {{ appointment.advisor.name }}
        </span>
        <span v-if="appointment.advisor.title" :id="`appointment-${appointment.id}-advisor-role`" class="text-dark">
          - {{ appointment.advisor.title }}
        </span>
      </div>
      <div v-if="size(appointment.advisor.departments)" class="text-secondary">
        <span v-for="(dept, index) in appointment.advisor.departments" :key="dept.code">
          <span :id="`appointment-${appointment.id}-advisor-dept-${index}`">{{ dept.name }}</span>
        </span>
      </div>
      <div v-if="appointment.appointmentType" :id="`appointment-${appointment.id}-type`" class="mt-3">
        {{ appointment.appointmentType }}
      </div>
      <div v-if="appointment.topics && size(appointment.topics)">
        <div class="pill-list-header mt-3 mb-1">{{ size(appointment.topics) === 1 ? 'Topic' : 'Topics' }}</div>
        <ul class="pill-list pl-0">
          <li
            v-for="(topic, index) in appointment.topics"
            :id="`appointment-${appointment.id}-topic-${index}`"
            :key="topic"
            class="mt-2">
            <span class="pill pill-attachment text-uppercase text-nowrap">{{ topic }}</span>
          </li>
        </ul>
      </div>
      <div>
        <ul class="pill-list pl-0 mt-3">
          <li
            v-for="(attachment, index) in appointment.attachments"
            :id="`appointment-${appointment.id}-attachment-${index}`"
            :key="attachment.name"
            class="mt-2">
            <span class="pill pill-attachment text-nowrap">
              <a
                :id="`appointment-${appointment.id}-attachment-${index}`"
                :href="downloadUrl(attachment)">
                <font-awesome icon="paperclip" />
                {{ attachment.displayName }}
              </a>
            </span>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
import DropInAppointmentDropdown from '@/components/appointment/DropInAppointmentDropdown'
import Context from '@/mixins/Context'
import Util from '@/mixins/Util'
import { getCalnetProfileByUid } from '@/api/user'

export default {
  name: 'AdvisingAppointment',
  components: { DropInAppointmentDropdown },
  mixins: [Context, Util],
  props: {
    isOpen: {
      required: true,
      type: Boolean
    },
    appointment: {
      required: true,
      type: Object
    },
    onAppointmentStatusChange: {
      required: true,
      type: Function
    },
    student: {
      required: true,
      type: Object
    }
  },
  watch: {
    isOpen() {
      this.setAdvisor()
    }
  },
  created() {
    this.setAdvisor()
  },
  methods: {
    datePerTimezone(date) {
      return this.$moment(date).tz(this.$config.timezone)
    },
    downloadUrl(attachment) {
      return `${this.$config.apiBaseUrl}/api/appointments/attachment/${attachment.id}`
    },
    isUserDropInAdvisor(deptCode) {
      const deptCodes = this.map(this.$currentUser.dropInAdvisorStatus || [], 'deptCode')
      return this.$_.includes(deptCodes, this.$_.upperCase(deptCode))
    },
    setAdvisor() {
      const requiresLazyLoad = this.isOpen && (!this.$_.get(this.appointment, 'advisor.name') || !this.$_.get(this.appointment, 'advisor.title'))
      if (requiresLazyLoad) {
        if (this.$_.get(this.appointment, 'advisor.uid')) {
          const advisor_uid = this.appointment.advisor.uid
          if (advisor_uid) {
            if (advisor_uid === this.$currentUser.uid) {
              // TODO: do not mutate prop
              this.appointment.advisor = this.$currentUser  // eslint-disable-line vue/no-mutating-props
            } else {
              getCalnetProfileByUid(advisor_uid).then(data => {
                // TODO: do not mutate prop
                this.appointment.advisor = data  // eslint-disable-line vue/no-mutating-props
              })
            }
          }
        }
      }
    },
  }
}
</script>

<style scoped>
.advising-appointment-outer {
  flex-basis: 100%;
}
.status-arrived-icon {
  color: #f0ad4e;
  width: 18px;
}
.status-cancelled-icon {
  color: #f0ad4e;
  width: 18px;
}
.status-checked-in-icon {
  color: #00c13a;
  width: 18px;
}
</style>
