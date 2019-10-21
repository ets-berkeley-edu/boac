<template>
  <div class="ml-3 mr-3 mt-3">
    <Spinner />
    <div v-if="!loading" class="waitlist-container">
      <DropInWaitlist :dept-code="deptCode" :waitlist="waitlist" />
    </div>
  </div>
</template>

<script>
import DropInWaitlist from "@/components/appointment/DropInWaitlist";
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments';

export default {
  name: 'AppointmentWaitlist',
  components: {DropInWaitlist, Spinner},
  mixins: [Loading, UserMetadata, Util],
  data: () => ({
    waitlist: undefined
  }),
  created() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    getDropInAppointmentWaitlist(this.deptCode).then(waitlist => {
      this.waitlist = waitlist;
      this.loaded();
    });
  }
}
</script>

<style scoped>
.waitlist-container {
  margin: 0 auto;
  max-width: 480px;
}
</style>
