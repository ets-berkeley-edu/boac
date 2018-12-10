<template>
  <div class="home-container">
    <Spinner/>
    <div v-if="!loading">
      <h1>BOAC Flight Deck</h1>
      <DemoModeToggle/>

      <h2 class="page-section-header-sub">Users</h2>
      <b-card no-body>
        <b-tabs pills card no-key-nav>
          <b-tab :title="group.name" v-for="group in userGroups" v-bind:key="group.name">
            <b-container fluid>
              <b-row v-for="groupUser in group.users"
                     v-bind:key="groupUser.uid">
                <b-col sm="auto"
                       class="pr-0"
                       v-bind:class="{'pb-2': groupUser.uid === user.uid}">
                  <a v-bind:class="{'faint-text pb-2': groupUser.uid === user.uid}"
                     :aria-label="'Go to UC Berkeley Directory page of ' + groupUser.name"
                     :href="'https://www.berkeley.edu/directory/results?search-term=' + groupUser.name"
                     target="_blank">{{groupUser.name}}</a>
                </b-col>
                <b-col v-if="groupUser.uid !== user.uid">
                  <b-btn :id="'become-' + groupUser.uid"
                         class="mb-1 p-0"
                         :title="'Log in as ' + groupUser.name"
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
import _ from 'lodash';
import AppConfig from '@/mixins/AppConfig';
import DemoModeToggle from '@/components/admin/DemoModeToggle.vue';
import Loading from '@/mixins/Loading.vue';
import Spinner from '@/components/Spinner.vue';
import UserMetadata from '@/mixins/UserMetadata';
import { becomeUser, getAuthorizedUserGroups } from '@/api/user';

export default {
  name: 'Admin',
  mixins: [AppConfig, Loading, UserMetadata],
  components: {
    DemoModeToggle,
    Spinner
  },
  created() {
    this.loadUserGroups();
  },
  data: () => ({
    active: [],
    userGroups: []
  }),
  methods: {
    loadUserGroups() {
      getAuthorizedUserGroups().then(data => {
        this.userGroups = data;
        _.each(this.userGroups, group => {
          _.each(_.orderBy(group.users, 'name'), user => {
            user.id = user.uid;
            user.name = user.firstName + ' ' + user.lastName;
          });
        });
        this.loaded();
      });
    },
    become(uid) {
      becomeUser(uid).then(() => (window.location = '/home'));
    }
  }
};
</script>
