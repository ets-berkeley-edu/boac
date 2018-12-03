<template>
  <div v-if="user">
    <b-dropdown id="header-dropdown-under-name"
                class="mr-3"
                variant="link"
                no-caret
                right>
      <template slot="button-content">
        <div class="d-flex align-items-center">
          <div class="b-link-text">{{ user.firstName }}</div><i class="ml-1 fas fa-caret-down b-link-text"></i>
        </div>
      </template>
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
.b-link-text {
  color: #fff;
  text-decoration: none !important;
}
</style>
