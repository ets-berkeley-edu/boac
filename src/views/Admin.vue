<template>
  <div class="p-3">
    <Spinner alert-prefix="The Admin page" />
    <div v-if="!loading">
      <div class="align-items-center d-flex pb-3">
        <div class="pr-3">
          <font-awesome :style="{ color: '#3b7ea5' }" icon="plane-departure" size="2x" />
        </div>
        <div class="pt-2">
          <h1 class="page-section-header">BOA Flight Deck</h1>
        </div>
      </div>
      <div class="pt-2">
        <h2 class="page-section-header-sub">My Profile</h2>
        <MyProfile class="mt-2" />
      </div>
      <div v-if="$config.isDemoModeAvailable">
        <div class="pt-3">
          <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
        </div>
        <DemoModeToggle />
      </div>
      <div v-if="dropInSchedulingDepartments.length">
        <DropInSchedulerManagement
          v-for="dept in dropInSchedulingDepartments"
          :key="dept.code"
          :dept="dept" />
      </div>
      <div v-if="$currentUser.isAdmin">
        <EditServiceAnnouncement />
      </div>
      <div v-if="$currentUser.isAdmin">
        <Status />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DemoModeToggle from '@/components/admin/DemoModeToggle';
import DropInSchedulerManagement from '@/components/admin/DropInSchedulerManagement';
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement';
import Loading from '@/mixins/Loading';
import MyProfile from '@/components/admin/MyProfile';
import Spinner from '@/components/util/Spinner';
import Status from '@/components/util/Status';
import Util from '@/mixins/Util';
import { getDropInSchedulers } from '@/api/user';

export default {
  name: 'Admin',
  components: {
    DropInSchedulerManagement,
    DemoModeToggle,
    EditServiceAnnouncement,
    MyProfile,
    Spinner,
    Status
  },
  mixins: [Context, Loading, Util],
  data: () => ({
    dropInSchedulingDepartments: []
  }),
  created() {
    if (this.$currentUser.canAccessAdvisingData) {
      getDropInSchedulers().then(departments => {
        this.dropInSchedulingDepartments = departments;
      });
    }
  },
  mounted() {
    this.loaded('Flight Deck');
  }
};
</script>
