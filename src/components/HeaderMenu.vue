<template>
  <div>
    <div v-if="!user"><i class="fas fa-spinner fa-spin b-link-text mr-4"></i></div>
    <div v-if="user">
      <span v-if="user && !user.firstName">{{ user }}</span>
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
        <b-dropdown-item href="#" v-if="user.isAdmin"><router-link to="/admin" tag="span">Admin</router-link></b-dropdown-item>
        <b-dropdown-item href="#" v-on:click="logOut">Log Out</b-dropdown-item>
        <b-dropdown-item :href="'mailto:' + supportEmailAddress" target="_blank">Feedback/Help</b-dropdown-item>
      </b-dropdown>
    </div>
  </div>
</template>

<script>
import AppConfig from '@/mixins/AppConfig';
import UserMetadata from '@/mixins/UserMetadata';
import store from '@/store';
import { getCasLogoutURL } from '@/api/user';

export default {
  name: 'HeaderMenu',
  mixins: [AppConfig, UserMetadata],
  methods: {
    logOut() {
      getCasLogoutURL().then(data => {
        store.commit('logout');
        window.location.href = data.casLogoutURL;
      });
    }
  }
};
</script>

<style scoped>
.b-link-text {
  color: #fff;
}
</style>
