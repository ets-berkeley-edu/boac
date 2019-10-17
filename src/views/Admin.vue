<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <h1>BOA Flight Deck</h1>
      <div class="pt-2">
        <h2 class="page-section-header-sub">My Profile</h2>
        <MyProfile class="mt-2" />
      </div>
      <div v-if="isDemoModeAvailable">
        <div class="pt-3">
          <h2 class="mb-0 page-section-header-sub">Demo Mode</h2>
        </div>
        <DemoModeToggle />
      </div>
      <div v-if="user.isAdmin">
        <EditServiceAnnouncement />
      </div>
      <div v-if="user.isAdmin">
        <Status />
      </div>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DemoModeToggle from '@/components/admin/DemoModeToggle';
import EditServiceAnnouncement from '@/components/admin/EditServiceAnnouncement';
import Loading from '@/mixins/Loading';
import MyProfile from '@/components/admin/MyProfile';
import Spinner from '@/components/util/Spinner';
import Status from '@/components/util/Status';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';

export default {
  name: 'Admin',
  components: {
    DemoModeToggle,
    EditServiceAnnouncement,
    MyProfile,
    Spinner,
    Status
  },
  mixins: [Context, Loading, UserMetadata, Util],
  mounted() {
    this.loaded();
  }
};
</script>
