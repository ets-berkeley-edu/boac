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
      <div v-if="includes(dropInAdvisorDeptCodes(), appointment.deptCode)" class="d-flex align-items-center">
        <div>
          <b-dropdown
            class="bg-white mb-3 mr-3 mt-3"
            split
            :disabled="!!appointment.checkedInBy || !!appointment.canceledAt"
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
          <font-awesome icon="calendar-check" class="status-checked-in-icon" /> Check In <span v-if="appointment.arrivalTime">@ {{ appointment.arrivalTime }}</span>
        </div>
        <div v-if="appointment.canceledAt">
          <font-awesome icon="calendar-minus" class="status-canceled-icon" /> Canceled
        </div>
      </div>
      <div v-if="!isUndefined(appointment.author) && !appointment.author.name" class="mt-2 advisor-profile-not-found">
        Advisor profile not found
      </div>
      <div v-if="appointment.author" class="mt-2">
        <div v-if="appointment.author.name">
          <span class="sr-only">Appointment created by </span>
          <a
            v-if="appointment.author.uid"
            :id="`appointment-${appointment.id}-author-name`"
            :aria-label="`Open UC Berkeley Directory page of ${appointment.author.name} in a new window`"
            :href="`https://www.berkeley.edu/directory/results?search-term=${appointment.author.name}`"
            target="_blank">{{ appointment.author.name }}</a>
          <span v-if="!appointment.author.uid" :id="`appointment-${appointment.id}-author-name`">
            {{ appointment.author.name }}
          </span>
          <span v-if="appointment.author.role">
            - <span :id="`appointment-${appointment.id}-author-role`" class="text-dark">{{ appointment.author.role }}</span>
          </span>
        </div>
        <div v-if="size(appointment.author.departments)" class="text-secondary">
          <span v-if="appointment.author.title">{{ appointment.author.title }}, </span><span v-if="size(appointment.author.departments)">
            {{ oxfordJoin(map(appointment.author.departments, 'name')) }}
          </span>
        </div>
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
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingAppointment',
  components: {AppointmentCancellationModal},
  mixins: [UserMetadata, Util],
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
  methods: {
    appointmentCancellation(appointmentId, cancelReason, cancelReasonExplained) {
      this.cancelAppointment(appointmentId, cancelReason, cancelReasonExplained);
      this.showCancelAppointmentModal = false;
    },
    closeCancellationModal() {
      this.showCancelAppointmentModal = false;
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
