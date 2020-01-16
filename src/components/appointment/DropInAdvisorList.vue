<template>
  <div>
    <div class="border-bottom d-flex justify-content-between">
      <div>
        <h2 class="font-size-18 font-weight-bold text-nowrap">Advisors</h2>
      </div>
      <div>
        <h2 class="font-size-18 font-weight-bold text-nowrap">Availability Status</h2>
      </div>
    </div>
    <div v-if="!advisors.length" class="border-bottom">
      <div
        id="no-advisors"
        class="font-size-16 mb-3 ml-1 mt-3"
        aria-live="polite"
        role="alert">
        No advisors found
      </div>
    </div>
    <div v-if="advisors.length">
      <b-container fluid class="pl-0 pr-0">
        <div
          v-for="advisor in orderedAdvisors"
          :key="advisor.uid"
          no-gutters
          class="border-bottom font-size-16 d-flex justify-content-between">
          <div class="d-flex align-items-center text-nowrap">
            {{ advisor.name }}
          </div>
          <div>
            <DropInAvailabilityToggle
              :dept-code="deptCode"
              :is-homepage="false"
              :reserved-appointments="reservedAppointmentsByAdvisor[advisor.uid] || []"
              :status="advisor.status"
              :uid="advisor.uid" />
          </div>
        </div>
      </b-container>
    </div>
  </div>
</template>

<script>
import Berkeley from '@/mixins/Berkeley';
import Context from '@/mixins/Context';
import DropInAvailabilityToggle from '@/components/appointment/DropInAvailabilityToggle';
import Util from '@/mixins/Util';

export default {
  name: 'DropInAdvisorList',
  components: {
    DropInAvailabilityToggle,
  },
  mixins: [Berkeley, Context, Util],
  props: {
    advisors: {
      type: Array,
      required: true
    },
    deptCode: {
      type: String,
      required: true
    },
    waitlist: {
      type: Object,
      required: true
    }
  },
  computed: {
    reservedAppointmentsByAdvisor: function() {
      return this.groupBy(this.waitlist.unresolved, (appt) => {
        return appt.status === 'reserved' && appt.advisorUid;
      });
    },
    orderedAdvisors: function() {
      return this.orderBy(this.advisors, 'name');
    }
  }
}
</script>

<style scoped>
.supervisor-on-call-icon {
  color: #f0ad4e;
}
</style>
