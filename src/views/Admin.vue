<template>
  <div class="p-3">
    <Spinner />
    <div v-if="!loading">
      <span
        role="alert"
        aria-live="passive"
        class="sr-only">Admin page loaded</span>
      <h1>BOAC Flight Deck</h1>
      <div v-if="user.isAdmin && devAuthEnabled" class="d-flex flex-row mt-3 mb-3">
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

      <h2 class="page-section-header-sub pb-2">Users</h2>
      <b-card no-body>
        <b-tabs pills card>
          <b-tab v-for="group in userGroups" :key="group.name" :title="group.name">
            <b-container fluid>
              <b-row
                v-for="groupUser in group.users"
                :key="groupUser.id">
                <b-col
                  sm="auto"
                  class="pr-0"
                  :class="{'pb-2': groupUser.uid === user.uid}">
                  <a
                    :class="{'faint-text pb-2': groupUser.uid === user.uid}"
                    :aria-label="`Go to UC Berkeley Directory page of ${groupUser.name}`"
                    :href="`https://www.berkeley.edu/directory/results?search-term=${groupUser.name}`"
                    target="_blank">{{ groupUser.name }}</a>
                </b-col>
                <b-col v-if="groupUser.uid !== user.uid">
                  <b-btn
                    v-if="devAuthEnabled"
                    :id="'become-' + groupUser.uid"
                    class="mb-1 p-0"
                    :title="`Log in as ${groupUser.name}`"
                    variant="link"
                    @click="become(groupUser.uid)">
                    <i class="fas fa-sign-in-alt"></i>
                  </b-btn>
                </b-col>
              </b-row>
            </b-container>
          </b-tab>
        </b-tabs>
      </b-card>

      <Status />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DemoModeToggle from '@/components/admin/DemoModeToggle';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import Status from '@/components/util/Status';
import store from '@/store';
import UserMetadata from '@/mixins/UserMetadata';
import { becomeUser } from '@/api/user';

export default {
  name: 'Admin',
  components: {
    DemoModeToggle,
    Spinner,
    Status
  },
  mixins: [Context, Loading, UserMetadata],
  data: () => ({
    active: [],
    blurAvatarUrl: require('@/assets/sampleBlurAvatar.jpg'),
    userGroups: null
  }),
  watch: {
    user: function() {
      this.updateLoadingStatus();
    }
  },
  created() {
    store.dispatch('user/loadUserGroups').then(data => {
      this.userGroups = data;
      this.updateLoadingStatus();
    });
  },
  methods: {
    updateLoadingStatus() {
      if (this.loading && this.user && this.userGroups) {
        this.loaded();
      }
    },
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    }
  }
};
</script>
