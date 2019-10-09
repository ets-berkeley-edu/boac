<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <h1>BOA Flight Deck</h1>
      <div v-if="isDemoModeAvailable" class="d-flex flex-row mt-3 mb-3">
        <div class="mr-3">
          <img
            id="avatar-verify-blur"
            class="avatar student-avatar-large"
            :class="{'img-blur': user.inDemoMode}"
            :src="blurAvatarUrl" />
        </div>
        <div>
          <div>
            <DemoModeToggle />
          </div>
          <div class="faint-text pt-2">
            In demo mode, student profile pictures and sensitive data will be blurred.
          </div>
        </div>
      </div>
      <Users 
        v-if="users"
        :users="users" />
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
import Spinner from '@/components/util/Spinner';
import Status from '@/components/util/Status';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import Users from '@/components/admin/Users';
import Util from '@/mixins/Util';

export default {
  name: 'Admin',
  components: {
    DemoModeToggle,
    EditServiceAnnouncement,
    Users,
    Spinner,
    Status
  },
  mixins: [Context, Loading, UserMetadata, Util],
  data: () => ({
    active: [],
    blurAvatarUrl: require('@/assets/sampleBlurAvatar.jpg'),
    users: null
  }),
  mounted() {
    if (this.user.isAdmin) {
      store.dispatch('user/loadUsers').then(data => {
        this.users = data;
        this.loaded();
      });
    } else {
      this.loaded();
    }
  }
};
</script>

<style scoped>
  .users-row {
    height: 32px;
  }
</style>
