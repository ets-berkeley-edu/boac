<template>
  <div class="home-container">
    <Spinner/>
    <div v-if="!loading">
      <h1>BOAC Flight Deck</h1>
      <DemoModeToggle/>
      <h2 class="page-section-header-sub">Users</h2>
      <v-treeview
          :items="userGroups"
          item-key="code"
          item-children="users"></v-treeview>
    </div>
  </div>
</template>

<script>
import _ from 'lodash';
import { becomeUser, getAuthorizedUserGroups } from '@/api/user';
import DemoModeToggle from '@/components/DemoModeToggle.vue';
import Spinner from '@/components/Spinner.vue';
import Loading from '@/mixins/Loading.vue';

export default {
  name: 'Admin',
  mixins: [Loading],
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
          _.each(group.users, user => {
            user.id = user.uid;
            user.name = user.firstName + ' ' + user.lastName;
          });
        });
        this.loaded();
      });
    },
    selected(uid) {
      becomeUser(uid).then(() => {
        window.location = '/home';
      });
    }
  }
};
</script>
