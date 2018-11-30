<template>
  <div v-if="user">
    <b-dropdown id="ddown-right"
                right
                :text="user.firstName"
                variant="link">
      <b-dropdown-item href="/admin" v:if="user.isAdmin">Admin</b-dropdown-item>
      <b-dropdown-item href="#" v-on:click="logOut">Log Out</b-dropdown-item>
      <b-dropdown-item :href="'mailto:' + supportEmailAddress" target="_blank">Feedback/Help</b-dropdown-item>
    </b-dropdown>
  </div>
</template>

<script>
import _ from 'lodash';
import { getCasLogoutURL } from '@/api/user';
import store from '@/store';

export default {
  name: 'HeaderMenu',
  computed: {
    user() {
      return store.getters.user;
    },
    supportEmailAddress() {
      return _.get(store.getters.config, 'supportEmailAddress');
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

<style scoped>
.header-btn-label {
  font-size: 16px;
  text-transform: none;
}
.header-btn-label span {
  padding-right: 6px;
}
.header-menu-content {
  background-color: white;
}
</style>
