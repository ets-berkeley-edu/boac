<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner alert-prefix="Appointment waitlist" />
    <div v-if="!loading" class="mb-4 pb-3 pt-3 text-center">
      <b-btn
        id="btn-create-appointment"
        @click="$refs.dropInWaitlist.openCreateAppointmentModal()"
        variant="primary"
        class="btn-primary-color-override pl-3 pr-3"
        aria-label="Create appointment. Modal window will open.">
        New Drop-in Appointment
      </b-btn>
    </div>
    <div v-if="!loading" class="drop-in-desk-outer">
      <div class="waitlist-container">
        <DropInAdvisorList
          :dept-code="deptCode"
          :advisors="advisors" />
      </div>
      <div class="waitlist-container">
        <DropInWaitlist
          ref="dropInWaitlist"
          :dept-code="deptCode"
          :on-appointment-status-change="loadDropInWaitlist"
          :waitlist="waitlist" />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DropInAdvisorList from '@/components/appointment/DropInAdvisorList';
import DropInWaitlist from '@/components/appointment/DropInWaitlist';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments';

export default {
  name: 'DropInDesk',
  components: {DropInAdvisorList, DropInWaitlist, Spinner},
  mixins: [Context, Loading, UserMetadata, Util],
  data: () => ({
    advisors: undefined,
    waitlist: undefined
  }),
  created() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    this.loadDropInWaitlist();
    setInterval(this.loadDropInWaitlist, this.apptDeskRefreshInterval);
  },
  methods: {
    loadDropInWaitlist() {
      getDropInAppointmentWaitlist(this.deptCode).then(response => {
        let announceUpdate = false;
        if (!this.isEqual(response.advisors, this.advisors)) {
          if (this.advisors) {
            announceUpdate = true;
          }
          this.advisors = response.advisors;
        }
        if (!this.isEqual(response.waitlist, this.waitlist)) {
          if (this.waitlist) {
            announceUpdate = true;
          }
          this.waitlist = response.waitlist;
        }
        if (announceUpdate) {
          this.alertScreenReader("The drop-in waitlist has been updated");
        } else if (response.waitlist) {
          this.loaded('Appointment waitlist');
        }
      });
    }
  }
}
</script>

<style scoped>
.drop-in-desk-outer {
  display: flex;
}
.waitlist-container {
  margin: 0 auto;
  width: 480px;
}
</style>
