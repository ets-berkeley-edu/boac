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
      <div v-if="isUserDropInAdvisor()" class="d-flex align-items-center">
        <div>
          <b-dropdown
            class="bg-white mb-3 mr-3 mt-3"
            split
            :disabled="includes(['canceled', 'checkedIn'], appointment.status)"
            text="Check In"
            variant="outline-dark"
            @click="checkIn(appointment.id)">
            <b-dropdown-item-button @click="cancelAppointment(appointment.id)">Cancel</b-dropdown-item-button>
          </b-dropdown>
        </div>
        <div v-if="appointment.status === 'checkedIn'">
          <font-awesome icon="calendar-check" class="status-checked-in-icon" /> Check In <span v-if="appointment.arrivalTime">@ {{ appointment.arrivalTime }}</span>
        </div>
        <div v-if="appointment.status === 'canceled'">
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
      <div>
        {{ appointment.reason }}
      </div>
    </div>
  </div>
</template>

<script>
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'AdvisingAppointment',
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
  methods: {
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
