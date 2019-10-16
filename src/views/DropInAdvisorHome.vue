<template>
  <div class="ml-3 mt-3">
    <h1 class="sr-only">Welcome to BOA</h1>
    <Spinner />
    <div v-if="!loading" class="home-content">
      <div class="d-flex justify-content-between">
        <div class="column-01">
          <DropInWaitlist :dept-code="deptCode" :is-homepage="true" :waitlist="waitlist" />
        </div>
        <div class="mr-2">
          <div>
            <h2>Alerts</h2>
            <div>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
              dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
              ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
              fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
              mollit anim id est laborum.
            </div>
          </div>
          <div class="mt-4">
            <h2>Advising Resources</h2>
            <div>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
              dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip
              ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
              fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
              mollit anim id est laborum.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import DropInWaitlist from "@/components/appointment/DropInWaitlist";
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Util from '@/mixins/Util';
import { getDropInAppointmentWaitlist } from '@/api/appointments'

export default {
  name: 'DropInAdvisorHome',
  components: {DropInWaitlist, Spinner},
  mixins: [Loading, Util],
  data: () => ({
    deptCode: undefined,
    waitlist: undefined
  }),
  mounted() {
    this.deptCode = this.get(this.$route, 'params.deptCode');
    getDropInAppointmentWaitlist(this.deptCode).then(waitlist => {
      this.waitlist = waitlist;
      this.loaded();
    });
  }
}
</script>

<style scoped>
.column-01 {
  max-width: 48%;
  min-width: 48%;
  margin-right: 30px;
}
</style>

<style>
.homepage-header-border {
  border-bottom-color: lightgrey;
  border-bottom-style: solid;
  border-bottom-width: 4px;
}
</style>
