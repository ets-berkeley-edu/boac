<template>
  <md-menu md-direction="bottom-end"
           md-size="small">
    <md-button class="header-btn-label no-wrap"
               md-menu-trigger>
      <span v-if="user">{{ user.firstName }}</span>
      <i v-bind:class="{'fas fa-caret-down': user, 'fas fa-spinner fa-spin': !user}"></i>
    </md-button>
    <md-menu-content class="header-menu-content" v-if="user">
      <md-menu-item href><router-link to="/admin">Admin</router-link></md-menu-item>
      <md-menu-item href="#" v-on:click="logOut">Log Out</md-menu-item>
      <md-menu-item :href="'mailto:' + supportEmailAddress" target="_blank">Feedback/Help</md-menu-item>
    </md-menu-content>
  </md-menu>
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
