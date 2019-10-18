<template>
  <div :id="`appointment-${appointment.id}-outer`" class="advising-appointment-outer">
    <div
      v-if="!isOpen"
      :id="`appointment-${appointment.id}-is-closed`"
      :class="{'truncate-with-ellipsis': !isOpen}"
      title="Advising appointment">
      <span :id="`appointment-${appointment.id}-reason-closed`">{{ appointment.details }}</span>
    </div>
    <div v-if="isOpen" :id="`appointment-${appointment.id}-is-open`">
      <div class="mt-2">
        <span :id="`appointment-${appointment.id}-details`" v-html="appointment.details"></span>
      </div>
      <div class="d-flex align-items-center mt-3 mb-3">
        <div v-if="checkInAvailable">
          <b-dropdown
            class="bg-white mr-3"
            split
            text="Check In"
            variant="outline-dark"
            @click="checkIn(appointment.id)">
            <b-dropdown-item-button @click="showCancelAppointmentModal = true">Cancel</b-dropdown-item-button>
          </b-dropdown>
          <AppointmentCancellationModal
            v-if="showCancelAppointmentModal"
            :appointment="appointment"
            :appointment-cancellation="appointmentCancellation"
            :close="closeCancellationModal"
            :show-modal="showCancelAppointmentModal"
            :student="student" />
        </div>
        <div v-if="!!appointment.checkedInBy">
          <font-awesome icon="calendar-check" class="status-checked-in-icon" />
          <span class="text-secondary ml-1">
            Check In
            <span v-if="appointment.checkedInAt">
              @ {{ datePerTimezone(appointment.checkedInAt) | moment('h:mma') }}
            </span>
          </span>
        </div>
        <div v-if="appointment.canceledAt">
          <div>
            <font-awesome icon="calendar-minus" class="status-canceled-icon" />
            <span class="text-secondary ml-1">
              {{ appointment.cancelReason || 'Canceled' }}
            </span>
          </div>
          <div v-if="appointment.cancelReasonExplained" class="mt-1">
            {{ appointment.cancelReasonExplained }}
          </div>
        </div>
      </div>
      <div v-if="appointment.advisorName" class="mt-2">
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
import AppointmentCancellationModal from '@/components/appointment/AppointmentCancellationModal';
import Context from '@/mixins/Context';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingAppointment',
  components: {AppointmentCancellationModal},
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
    cancelAppointment: {
      required: true,
      type: Function
    },
    checkIn: {
      required: true,
      type: Function
    },
    student: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    showCancelAppointmentModal: false
  }),
  computed: {
    checkInAvailable() {
      return (
        this.includes(this.dropInAdvisorDeptCodes(), this.appointment.deptCode) &&
        !this.appointment.checkedInBy &&
        !this.appointment.canceledAt
      );
    }
  },
  methods: {
    appointmentCancellation(appointmentId, cancelReason, cancelReasonExplained) {
      this.cancelAppointment(appointmentId, cancelReason, cancelReasonExplained);
      this.showCancelAppointmentModal = false;
    },
    closeCancellationModal() {
      this.showCancelAppointmentModal = false;
    },
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
.advisor-profile-not-found {
  color: #999;
  font-size: 14px;
}
.status-canceled-icon {
  color: #f0ad4e;
}
.status-checked-in-icon {
  color: #00c13a;
}
</style>
