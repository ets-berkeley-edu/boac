<template>
  <v-menu offset-y v-if="user">
    <v-btn slot="activator">
      {{ user.firstName }}
    </v-btn>
    <v-list>
      <v-list-tile v-if="user.isAdmin">
        <v-list-tile-title>
          Admin
        </v-list-tile-title>
      </v-list-tile>
      <v-list-tile v-if="config">
        <v-list-tile-title>
          <a :href="`mailto:${config.supportEmailAddress}`" target="_blank">Feedback/Help</a>
        </v-list-tile-title>
      </v-list-tile>
    </v-list>
  </v-menu>
</template>

<script>
import { getCasLogoutURL } from '@/api/user';
import store from '@/store';

export default {
  name: 'HeaderMenu',
  computed: {
    config() {
      return store.getters.config;
    },
    user() {
      return store.getters.user;
    }
  },
  methods: {
    logOut() {
      getCasLogoutURL().then(data => {
        window.location.href = data.casLogoutURL;
      });
    }
  }
};
</script>
