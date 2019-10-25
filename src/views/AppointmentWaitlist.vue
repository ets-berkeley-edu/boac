<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner alert-prefix="Appointment waitlist" />
    <div v-if="!loading" class="waitlist-container">
      <DropInWaitlist :dept-code="deptCode" :waitlist="waitlist" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DropInWaitlist from "@/components/appointment/DropInWaitlist";
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments';

export default {
  name: 'AppointmentWaitlist',
  components: {DropInWaitlist, Spinner},
  mixins: [Context, Loading, UserMetadata, Util],
  data: () => ({
    waitlist: undefined
  }),
  created() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    this.loadDropInWaitlist();
    setInterval(this.loadDropInWaitlist, this.apptDeskRefreshInterval);
  },
  methods: {
    loadDropInWaitlist() {
      getDropInAppointmentWaitlist(this.deptCode).then(waitlist => {
        var announceUpdate = false;
        if (!this.isEqual(waitlist, this.waitlist)) {
          if (this.waitlist) {
            announceUpdate = true;
          }
          this.waitlist = waitlist;
        }
        this.loaded('Appointment waitlist');
        if (announceUpdate) {
          this.alertScreenReader("The drop-in waitlist has been updated");
        }
      });
    }
  }
}
</script>

<style scoped>
.waitlist-container {
  margin: 0 auto;
  max-width: 480px;
}
</style>
