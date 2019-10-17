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
      <div v-if="appointment.advisorName" class="mt-3">
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
