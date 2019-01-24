<template>
  <div class="p-3">
    <Spinner/>
    <div v-if="!loading">
      <span role="alert"
            aria-live="passive"
            class="sr-only">Admin page loaded</span>
      <h1>BOAC Flight Deck</h1>
      <div class="d-flex flex-row mt-3 mb-5">
        <div class="mr-3">
          <img id="avatar-verify-blur"
               class="avatar student-avatar-large"
               :class="{'img-blur': user.inDemoMode}"
               :src="blurAvatarUrl"/>
        </div>
        <div>
          <div>
            <DemoModeToggle/>
          </div>
          <div class="faint-text pt-2">
            In demo mode, student profile pictures and sensitive data will be blurred.
          </div>
        </div>
      </div>

      <h2 class="page-section-header-sub">Users</h2>
      <b-card no-body>
        <b-tabs pills card>
          <b-tab :title="group.name" v-for="group in userGroups" :key="group.name">
            <b-container fluid>
              <b-row v-for="groupUser in group.users"
                     :key="groupUser.id">
                <b-col sm="auto"
                       class="pr-0"
                       :class="{'pb-2': groupUser.uid === user.uid}">
                  <a :class="{'faint-text pb-2': groupUser.uid === user.uid}"
                     :aria-label="`Go to UC Berkeley Directory page of ${groupUser.name}`"
                     :href="`https://www.berkeley.edu/directory/results?search-term=${groupUser.name}`"
                     target="_blank">{{groupUser.name}}</a>
                </b-col>
                <b-col v-if="groupUser.uid !== user.uid">
                  <b-btn :id="'become-' + groupUser.uid"
                         class="mb-1 p-0"
                         :title="`Log in as ${groupUser.name}`"
                         variant="link"
                         v-on:click="become(groupUser.uid)"
                         v-if="devAuthEnabled"><i class="fas fa-sign-in-alt"></i></b-btn>
                </b-col>
              </b-row>
            </b-container>
          </b-tab>
        </b-tabs>
      </b-card>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context';
import DemoModeToggle from '@/components/admin/DemoModeToggle';
import Loading from '@/mixins/Loading';
import Spinner from '@/components/util/Spinner';
import UserMetadata from '@/mixins/UserMetadata';
import { becomeUser, getAuthorizedUserGroups } from '@/api/user';

export default {
  name: 'Admin',
  mixins: [Context, Loading, UserMetadata],
  components: {
    DemoModeToggle,
    Spinner
  },
  data: () => ({
    active: [],
    blurAvatarUrl: require('@/assets/sampleBlurAvatar.jpg'),
    userGroups: null
  }),
  created() {
    this.loadUserGroups();
  },
  methods: {
    loadUserGroups() {
      getAuthorizedUserGroups('firstName').then(data => {
        this.userGroups = data;
        this.updateLoadingStatus();
      });
    },
    updateLoadingStatus() {
      if (this.loading && this.user && this.userGroups) {
        this.loaded();
      }
    },
    become(uid) {
      becomeUser(uid).then(() => (window.location.href = '/home'));
    }
  },
  watch: {
    user: function() {
      this.updateLoadingStatus();
    }
  }
};
</script>
