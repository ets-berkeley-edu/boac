<template>
  <div :id="`appointment-${appointment.id}-outer`" class="advising-appointment-outer">
    <div
      v-if="!isOpen"
      :id="`appointment-${appointment.id}-is-closed`"
      :class="{'truncate-with-ellipsis': !isOpen}">
      <span :id="`appointment-${appointment.id}-details-closed`">{{ appointment.details }}</span>
    </div>
    <div v-if="isOpen" :id="`appointment-${appointment.id}-is-open`">
      <div class="mt-2">
        <span :id="`appointment-${appointment.id}-details`" v-html="appointment.details"></span>
      </div>
      <div class="d-flex align-items-center mt-3 mb-3">
        <div v-if="isUserDropInAdvisor(appointment.deptCode) && includes(['waiting', 'reserved'], appointment.status)">
          <DropInAppointmentDropdown
            :appointment="appointment"
            :dept-code="appointment.deptCode"
            :include-details-option="false"
            :on-appointment-status-change="onAppointmentStatusChange"
            :self-check-in="true"
            class="mr-3" />
        </div>
        <div v-if="appointment.status === 'reserved' && (user.isAdmin || isUserDropInAdvisor(appointment.deptCode))">
          <span class="text-secondary">
            Reserved
            <span v-if="appointment.statusBy" :id="`appointment-${appointment.id}-reserved-for`">
              for {{ appointment.statusBy.id === user.id ? 'you' : appointment.statusBy.name }}
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
        <div v-if="appointment.status === 'canceled'">
          <div>
            <font-awesome icon="calendar-minus" class="status-canceled-icon" />
            <span class="text-secondary ml-1">
              <span :id="`appointment-${appointment.id}-cancel-reason`">{{ appointment.cancelReason || 'Canceled' }}</span>
            </span>
          </div>
          <div v-if="appointment.cancelReasonExplained" class="mt-1">
            <span :id="`appointment-${appointment.id}-cancel-explained`">{{ appointment.cancelReasonExplained }}</span>
          </div>
        </div>
      </div>
      <div v-if="appointment.advisorName && (appointment.status === 'checked_in')" class="mt-2">
        <a
          v-if="appointment.advisorUid"
          :id="`appointment-${appointment.id}-advisor-name`"
          :aria-label="`Open UC Berkeley Directory page of ${appointment.advisorName} in a new window`"
          :href="`https://www.berkeley.edu/directory/results?search-term=${appointment.advisorName}`"
          target="_blank">{{ appointment.advisorName }}</a>
        <span v-if="!appointment.advisorUid" :id="`appointment-${appointment.id}-advisor-name`">
          {{ appointment.advisorName }}
        </span>
        <span v-if="appointment.advisorRole" :id="`appointment-${appointment.id}-advisor-role`" class="text-dark">
          - {{ appointment.advisorRole }}
        </span>
      </div>
      <div v-if="size(appointment.advisorDepartments)" class="text-secondary">
        <span v-for="(dept, index) in appointment.advisorDepartments" :key="dept.code">
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
    </div>
  </div>
</template>

<script>
import DropInAppointmentDropdown from '@/components/appointment/DropInAppointmentDropdown';
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingAppointment',
  components: { DropInAppointmentDropdown },
  mixins: [Context, UserMetadata, Util],
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
  methods: {
    datePerTimezone(date) {
      return this.$moment(date).tz(this.timezone);
    }
  }
}
</script>

<style scoped>
.advising-appointment-outer {
  flex-basis: 100%;
}
.status-canceled-icon {
  color: #f0ad4e;
}
.status-checked-in-icon {
  color: #00c13a;
}
</style>
