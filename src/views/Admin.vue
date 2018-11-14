<template>
  <div>
    <h1>BOAC Flight Deck</h1>
    <DemoModeToggle/>

    <h2>Users</h2>
    <v-treeview
        :items="userGroups"
        item-key="code"
        item-children="users"></v-treeview>
  </div>
</template>

<script>
import { becomeUser, getAuthorizedUserGroups } from '@/api/user';
import DemoModeToggle from '@/components/DemoModeToggle.vue';

export default {
  name: 'Admin',
  components: {
    DemoModeToggle
  },
  created() {
    this.loadUserGroups();
  },
  data: () => ({
    active: [],
    userGroups: []
  }),
  methods: {
    /* eslint no-undef: "warn" */
    loadUserGroups() {
      getAuthorizedUserGroups().then(data => {
        this.userGroups = data;
        _.each(this.userGroups, group => {
          _.each(group.users, user => {
            user.id = user.uid;
            user.name = user.firstName + ' ' + user.lastName;
          });
        });
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
